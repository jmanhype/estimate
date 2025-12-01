"""S3 storage client for file uploads and downloads."""

from typing import Any, BinaryIO

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError, NoCredentialsError

from src.core.config import settings

# S3 client (created lazily)
_s3_client: Any = None


def get_s3_client() -> Any:
    """
    Get or create S3 client.

    Returns:
        boto3.client: S3 client instance

    Example:
        s3 = get_s3_client()
        s3.upload_fileobj(file, bucket, key)
    """
    global _s3_client
    if _s3_client is None:
        # Configure with signature version for presigned URLs
        config = Config(signature_version="s3v4", region_name=settings.aws_region)

        # Create client with credentials
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            _s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name=settings.aws_region,
                config=config,
            )
        else:
            # Use default credential chain (IAM role, env vars, etc.)
            _s3_client = boto3.client("s3", region_name=settings.aws_region, config=config)

    return _s3_client


class StorageService:
    """
    Service for S3 storage operations.

    Provides methods for uploading, downloading, and managing files in S3.
    """

    def __init__(self, s3_client: Any = None) -> None:
        """
        Initialize storage service.

        Args:
            s3_client: Optional S3 client (uses default if not provided)
        """
        self.s3 = s3_client or get_s3_client()
        self.bucket = settings.s3_bucket_name

    def upload_file(self, file_obj: BinaryIO, key: str, content_type: str | None = None) -> str:
        """
        Upload file to S3.

        Args:
            file_obj: File object to upload
            key: S3 object key (path)
            content_type: Optional content type (e.g., "image/jpeg")

        Returns:
            str: S3 object URL

        Raises:
            StorageError: If upload fails

        Example:
            storage = StorageService()
            with open("photo.jpg", "rb") as f:
                url = storage.upload_file(f, "projects/123/photos/1.jpg", "image/jpeg")
        """
        try:
            extra_args = {}
            if content_type:
                extra_args["ContentType"] = content_type

            self.s3.upload_fileobj(file_obj, self.bucket, key, ExtraArgs=extra_args)

            return f"https://{self.bucket}.s3.{settings.aws_region}.amazonaws.com/{key}"

        except NoCredentialsError as e:
            raise StorageError("AWS credentials not found") from e
        except ClientError as e:
            raise StorageError(f"Failed to upload file: {e}") from e

    def download_file(self, key: str, file_obj: BinaryIO) -> None:
        """
        Download file from S3.

        Args:
            key: S3 object key (path)
            file_obj: File object to write to

        Raises:
            StorageError: If download fails

        Example:
            storage = StorageService()
            with open("downloaded.jpg", "wb") as f:
                storage.download_file("projects/123/photos/1.jpg", f)
        """
        try:
            self.s3.download_fileobj(self.bucket, key, file_obj)
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                raise StorageError(f"File not found: {key}") from e
            raise StorageError(f"Failed to download file: {e}") from e

    def delete_file(self, key: str) -> None:
        """
        Delete file from S3.

        Args:
            key: S3 object key (path)

        Raises:
            StorageError: If deletion fails

        Example:
            storage = StorageService()
            storage.delete_file("projects/123/photos/1.jpg")
        """
        try:
            self.s3.delete_object(Bucket=self.bucket, Key=key)
        except ClientError as e:
            raise StorageError(f"Failed to delete file: {e}") from e

    def delete_files(self, keys: list[str]) -> None:
        """
        Delete multiple files from S3.

        Args:
            keys: List of S3 object keys to delete

        Raises:
            StorageError: If deletion fails

        Example:
            storage = StorageService()
            storage.delete_files([
                "projects/123/photos/1.jpg",
                "projects/123/photos/2.jpg"
            ])
        """
        if not keys:
            return

        try:
            objects = [{"Key": key} for key in keys]
            self.s3.delete_objects(Bucket=self.bucket, Delete={"Objects": objects})
        except ClientError as e:
            raise StorageError(f"Failed to delete files: {e}") from e

    def file_exists(self, key: str) -> bool:
        """
        Check if file exists in S3.

        Args:
            key: S3 object key (path)

        Returns:
            bool: True if file exists

        Example:
            storage = StorageService()
            if storage.file_exists("projects/123/photos/1.jpg"):
                print("File exists")
        """
        try:
            self.s3.head_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            raise StorageError(f"Failed to check file existence: {e}") from e

    def get_file_size(self, key: str) -> int:
        """
        Get file size in bytes.

        Args:
            key: S3 object key (path)

        Returns:
            int: File size in bytes

        Raises:
            StorageError: If file not found or operation fails

        Example:
            storage = StorageService()
            size = storage.get_file_size("projects/123/photos/1.jpg")
            print(f"File size: {size / 1024 / 1024:.2f} MB")
        """
        try:
            response = self.s3.head_object(Bucket=self.bucket, Key=key)
            return int(response["ContentLength"])
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                raise StorageError(f"File not found: {key}") from e
            raise StorageError(f"Failed to get file size: {e}") from e

    def generate_presigned_url(
        self,
        key: str,
        operation: str = "get_object",
        expiration: int | None = None,
        content_type: str | None = None,
    ) -> str:
        """
        Generate presigned URL for file access.

        Args:
            key: S3 object key (path)
            operation: S3 operation (e.g., "get_object", "put_object")
            expiration: URL expiration in seconds (default from config)
            content_type: Content type for put_object operations

        Returns:
            str: Presigned URL

        Raises:
            StorageError: If URL generation fails

        Example:
            storage = StorageService()
            # Generate upload URL (expires in 1 hour)
            upload_url = storage.generate_presigned_url(
                "projects/123/photos/1.jpg",
                operation="put_object",
                content_type="image/jpeg"
            )
            # Generate download URL
            download_url = storage.generate_presigned_url("projects/123/photos/1.jpg")
        """
        try:
            params = {"Bucket": self.bucket, "Key": key}

            if operation == "put_object" and content_type:
                params["ContentType"] = content_type

            url = self.s3.generate_presigned_url(
                operation,
                Params=params,
                ExpiresIn=expiration or settings.s3_presigned_url_expiration,
            )

            return str(url)

        except ClientError as e:
            raise StorageError(f"Failed to generate presigned URL: {e}") from e

    def list_files(self, prefix: str, max_keys: int = 1000) -> list[str]:
        """
        List files with given prefix.

        Args:
            prefix: S3 key prefix (folder path)
            max_keys: Maximum number of keys to return

        Returns:
            list[str]: List of S3 object keys

        Example:
            storage = StorageService()
            # List all photos for project 123
            photos = storage.list_files("projects/123/photos/")
        """
        try:
            response = self.s3.list_objects_v2(
                Bucket=self.bucket, Prefix=prefix, MaxKeys=max_keys
            )

            if "Contents" not in response:
                return []

            return [obj["Key"] for obj in response["Contents"]]

        except ClientError as e:
            raise StorageError(f"Failed to list files: {e}") from e

    def copy_file(self, source_key: str, dest_key: str) -> None:
        """
        Copy file within S3.

        Args:
            source_key: Source S3 object key
            dest_key: Destination S3 object key

        Raises:
            StorageError: If copy fails

        Example:
            storage = StorageService()
            storage.copy_file(
                "projects/123/photos/temp/1.jpg",
                "projects/123/photos/1.jpg"
            )
        """
        try:
            copy_source = {"Bucket": self.bucket, "Key": source_key}
            self.s3.copy_object(CopySource=copy_source, Bucket=self.bucket, Key=dest_key)
        except ClientError as e:
            raise StorageError(f"Failed to copy file: {e}") from e

    def get_file_metadata(self, key: str) -> dict[str, str]:
        """
        Get file metadata.

        Args:
            key: S3 object key (path)

        Returns:
            dict: File metadata (content-type, size, last-modified, etc.)

        Raises:
            StorageError: If file not found or operation fails

        Example:
            storage = StorageService()
            metadata = storage.get_file_metadata("projects/123/photos/1.jpg")
            print(f"Content-Type: {metadata['ContentType']}")
            print(f"Last Modified: {metadata['LastModified']}")
        """
        try:
            response = self.s3.head_object(Bucket=self.bucket, Key=key)
            return {
                "ContentType": response.get("ContentType", ""),
                "ContentLength": response.get("ContentLength", 0),
                "LastModified": response.get("LastModified", ""),
                "ETag": response.get("ETag", ""),
            }
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                raise StorageError(f"File not found: {key}") from e
            raise StorageError(f"Failed to get file metadata: {e}") from e


class StorageError(Exception):
    """Exception raised for storage operation failures."""

    pass
