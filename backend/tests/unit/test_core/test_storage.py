"""Tests for S3 storage client."""

from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError, NoCredentialsError

from src.core.storage import StorageError, StorageService, get_s3_client


class TestS3Client:
    """Tests for S3 client initialization."""

    @patch("src.core.storage.boto3.client")
    def test_get_s3_client_with_credentials(self, mock_boto_client: MagicMock) -> None:
        """Test S3 client creation with explicit credentials."""
        with patch("src.core.storage.settings") as mock_settings:
            mock_settings.aws_access_key_id = "test_key"
            mock_settings.aws_secret_access_key = "test_secret"
            mock_settings.aws_region = "us-west-2"

            # Reset global client
            import src.core.storage
            src.core.storage._s3_client = None

            get_s3_client()

            mock_boto_client.assert_called_once()
            call_kwargs = mock_boto_client.call_args[1]
            assert call_kwargs["aws_access_key_id"] == "test_key"
            assert call_kwargs["aws_secret_access_key"] == "test_secret"
            assert call_kwargs["region_name"] == "us-west-2"

    @patch("src.core.storage.boto3.client")
    def test_get_s3_client_default_credentials(self, mock_boto_client: MagicMock) -> None:
        """Test S3 client creation with default credential chain."""
        with patch("src.core.storage.settings") as mock_settings:
            mock_settings.aws_access_key_id = ""
            mock_settings.aws_secret_access_key = ""
            mock_settings.aws_region = "us-east-1"

            # Reset global client
            import src.core.storage
            src.core.storage._s3_client = None

            get_s3_client()

            mock_boto_client.assert_called_once()
            call_kwargs = mock_boto_client.call_args[1]
            assert "aws_access_key_id" not in call_kwargs
            assert call_kwargs["region_name"] == "us-east-1"


class TestStorageService:
    """Tests for StorageService operations."""

    @pytest.fixture
    def mock_s3(self) -> MagicMock:
        """Create mock S3 client."""
        return MagicMock()

    @pytest.fixture
    def storage_service(self, mock_s3: MagicMock) -> StorageService:
        """Create StorageService with mock S3 client."""
        with patch("src.core.storage.settings") as mock_settings:
            mock_settings.s3_bucket_name = "test-bucket"
            mock_settings.aws_region = "us-east-1"
            mock_settings.s3_presigned_url_expiration = 3600
            return StorageService(s3_client=mock_s3)

    def test_upload_file(self, storage_service: StorageService, mock_s3: MagicMock) -> None:
        """Test uploading file to S3."""
        file_obj = BytesIO(b"test content")
        key = "projects/123/photo.jpg"

        url = storage_service.upload_file(file_obj, key, content_type="image/jpeg")

        assert url == "https://test-bucket.s3.us-east-1.amazonaws.com/projects/123/photo.jpg"
        mock_s3.upload_fileobj.assert_called_once_with(
            file_obj,
            "test-bucket",
            key,
            ExtraArgs={"ContentType": "image/jpeg"},
        )

    def test_upload_file_without_content_type(
        self, storage_service: StorageService, mock_s3: MagicMock
    ) -> None:
        """Test uploading file without content type."""
        file_obj = BytesIO(b"test content")
        key = "projects/123/file.bin"

        storage_service.upload_file(file_obj, key)

        mock_s3.upload_fileobj.assert_called_once_with(
            file_obj, "test-bucket", key, ExtraArgs={}
        )

    def test_upload_file_no_credentials(
        self, storage_service: StorageService, mock_s3: MagicMock
    ) -> None:
        """Test upload with missing credentials."""
        mock_s3.upload_fileobj.side_effect = NoCredentialsError()

        with pytest.raises(StorageError, match="AWS credentials not found"):
            storage_service.upload_file(BytesIO(b"test"), "test.jpg")

    def test_upload_file_client_error(
        self, storage_service: StorageService, mock_s3: MagicMock
    ) -> None:
        """Test upload with S3 client error."""
        mock_s3.upload_fileobj.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access denied"}},
            "upload_fileobj",
        )

        with pytest.raises(StorageError, match="Failed to upload file"):
            storage_service.upload_file(BytesIO(b"test"), "test.jpg")

    def test_download_file(
        self, storage_service: StorageService, mock_s3: MagicMock
    ) -> None:
        """Test downloading file from S3."""
        file_obj = BytesIO()
        key = "projects/123/photo.jpg"

        storage_service.download_file(key, file_obj)

        mock_s3.download_fileobj.assert_called_once_with("test-bucket", key, file_obj)

    def test_download_file_not_found(
        self, storage_service: StorageService, mock_s3: MagicMock
    ) -> None:
        """Test download when file doesn't exist."""
        mock_s3.download_fileobj.side_effect = ClientError(
            {"Error": {"Code": "404", "Message": "Not found"}}, "download_fileobj"
        )

        with pytest.raises(StorageError, match="File not found"):
            storage_service.download_file("missing.jpg", BytesIO())

    def test_download_file_client_error(
        self, storage_service: StorageService, mock_s3: MagicMock
    ) -> None:
        """Test download with S3 client error."""
        mock_s3.download_fileobj.side_effect = ClientError(
            {"Error": {"Code": "InternalError", "Message": "Server error"}},
            "download_fileobj",
        )

        with pytest.raises(StorageError, match="Failed to download file"):
            storage_service.download_file("test.jpg", BytesIO())

    def test_delete_file(
        self, storage_service: StorageService, mock_s3: MagicMock
    ) -> None:
        """Test deleting file from S3."""
        key = "projects/123/photo.jpg"

        storage_service.delete_file(key)

        mock_s3.delete_object.assert_called_once_with(Bucket="test-bucket", Key=key)

    def test_delete_file_error(
        self, storage_service: StorageService, mock_s3: MagicMock
    ) -> None:
        """Test delete with error."""
        mock_s3.delete_object.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access denied"}},
            "delete_object",
        )

        with pytest.raises(StorageError, match="Failed to delete file"):
            storage_service.delete_file("test.jpg")

    def test_delete_files(
        self, storage_service: StorageService, mock_s3: MagicMock
    ) -> None:
        """Test deleting multiple files."""
        keys = ["file1.jpg", "file2.jpg", "file3.jpg"]

        storage_service.delete_files(keys)

        mock_s3.delete_objects.assert_called_once()
        call_args = mock_s3.delete_objects.call_args[1]
        assert call_args["Bucket"] == "test-bucket"
        assert len(call_args["Delete"]["Objects"]) == 3

    def test_delete_files_empty_list(
        self, storage_service: StorageService, mock_s3: MagicMock
    ) -> None:
        """Test deleting empty list of files."""
        storage_service.delete_files([])

        mock_s3.delete_objects.assert_not_called()

    def test_file_exists_true(
        self, storage_service: StorageService, mock_s3: MagicMock
    ) -> None:
        """Test checking file existence (file exists)."""
        mock_s3.head_object.return_value = {"ContentLength": 1024}

        assert storage_service.file_exists("test.jpg") is True
        mock_s3.head_object.assert_called_once_with(Bucket="test-bucket", Key="test.jpg")

    def test_file_exists_false(
        self, storage_service: StorageService, mock_s3: MagicMock
    ) -> None:
        """Test checking file existence (file doesn't exist)."""
        mock_s3.head_object.side_effect = ClientError(
            {"Error": {"Code": "404", "Message": "Not found"}}, "head_object"
        )

        assert storage_service.file_exists("missing.jpg") is False

    def test_file_exists_error(
        self, storage_service: StorageService, mock_s3: MagicMock
    ) -> None:
        """Test file_exists with non-404 error."""
        mock_s3.head_object.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access denied"}},
            "head_object",
        )

        with pytest.raises(StorageError, match="Failed to check file existence"):
            storage_service.file_exists("test.jpg")

    def test_get_file_size(
        self, storage_service: StorageService, mock_s3: MagicMock
    ) -> None:
        """Test getting file size."""
        mock_s3.head_object.return_value = {"ContentLength": 2048}

        size = storage_service.get_file_size("test.jpg")

        assert size == 2048
        mock_s3.head_object.assert_called_once_with(Bucket="test-bucket", Key="test.jpg")

    def test_get_file_size_not_found(
        self, storage_service: StorageService, mock_s3: MagicMock
    ) -> None:
        """Test getting size of non-existent file."""
        mock_s3.head_object.side_effect = ClientError(
            {"Error": {"Code": "404", "Message": "Not found"}}, "head_object"
        )

        with pytest.raises(StorageError, match="File not found"):
            storage_service.get_file_size("missing.jpg")

    def test_generate_presigned_url_default(
        self, storage_service: StorageService, mock_s3: MagicMock
    ) -> None:
        """Test generating presigned URL with defaults."""
        mock_s3.generate_presigned_url.return_value = "https://presigned-url.com"

        url = storage_service.generate_presigned_url("test.jpg")

        assert url == "https://presigned-url.com"
        mock_s3.generate_presigned_url.assert_called_once_with(
            "get_object",
            Params={"Bucket": "test-bucket", "Key": "test.jpg"},
            ExpiresIn=3600,
        )

    def test_generate_presigned_url_put_with_content_type(
        self, storage_service: StorageService, mock_s3: MagicMock
    ) -> None:
        """Test generating presigned URL for upload."""
        mock_s3.generate_presigned_url.return_value = "https://upload-url.com"

        url = storage_service.generate_presigned_url(
            "test.jpg", operation="put_object", content_type="image/jpeg", expiration=600
        )

        assert url == "https://upload-url.com"
        call_args = mock_s3.generate_presigned_url.call_args
        assert call_args[0][0] == "put_object"
        assert call_args[1]["Params"]["ContentType"] == "image/jpeg"
        assert call_args[1]["ExpiresIn"] == 600

    def test_generate_presigned_url_error(
        self, storage_service: StorageService, mock_s3: MagicMock
    ) -> None:
        """Test presigned URL generation with error."""
        mock_s3.generate_presigned_url.side_effect = ClientError(
            {"Error": {"Code": "InternalError", "Message": "Error"}},
            "generate_presigned_url",
        )

        with pytest.raises(StorageError, match="Failed to generate presigned URL"):
            storage_service.generate_presigned_url("test.jpg")

    def test_list_files(self, storage_service: StorageService, mock_s3: MagicMock) -> None:
        """Test listing files with prefix."""
        mock_s3.list_objects_v2.return_value = {
            "Contents": [
                {"Key": "projects/123/photo1.jpg"},
                {"Key": "projects/123/photo2.jpg"},
                {"Key": "projects/123/photo3.jpg"},
            ]
        }

        files = storage_service.list_files("projects/123/")

        assert len(files) == 3
        assert "projects/123/photo1.jpg" in files
        mock_s3.list_objects_v2.assert_called_once_with(
            Bucket="test-bucket", Prefix="projects/123/", MaxKeys=1000
        )

    def test_list_files_empty(
        self, storage_service: StorageService, mock_s3: MagicMock
    ) -> None:
        """Test listing files with no results."""
        mock_s3.list_objects_v2.return_value = {}

        files = storage_service.list_files("empty/")

        assert files == []

    def test_list_files_error(
        self, storage_service: StorageService, mock_s3: MagicMock
    ) -> None:
        """Test list files with error."""
        mock_s3.list_objects_v2.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access denied"}},
            "list_objects_v2",
        )

        with pytest.raises(StorageError, match="Failed to list files"):
            storage_service.list_files("test/")

    def test_copy_file(self, storage_service: StorageService, mock_s3: MagicMock) -> None:
        """Test copying file within S3."""
        storage_service.copy_file("source/file.jpg", "dest/file.jpg")

        mock_s3.copy_object.assert_called_once()
        call_kwargs = mock_s3.copy_object.call_args[1]
        assert call_kwargs["CopySource"]["Bucket"] == "test-bucket"
        assert call_kwargs["CopySource"]["Key"] == "source/file.jpg"
        assert call_kwargs["Bucket"] == "test-bucket"
        assert call_kwargs["Key"] == "dest/file.jpg"

    def test_copy_file_error(
        self, storage_service: StorageService, mock_s3: MagicMock
    ) -> None:
        """Test copy file with error."""
        mock_s3.copy_object.side_effect = ClientError(
            {"Error": {"Code": "NoSuchKey", "Message": "Source not found"}},
            "copy_object",
        )

        with pytest.raises(StorageError, match="Failed to copy file"):
            storage_service.copy_file("missing.jpg", "dest.jpg")

    def test_get_file_metadata(
        self, storage_service: StorageService, mock_s3: MagicMock
    ) -> None:
        """Test getting file metadata."""
        from datetime import datetime

        mock_s3.head_object.return_value = {
            "ContentType": "image/jpeg",
            "ContentLength": 2048,
            "LastModified": datetime(2025, 1, 1, 12, 0, 0),
            "ETag": '"abc123"',
        }

        metadata = storage_service.get_file_metadata("test.jpg")

        assert metadata["ContentType"] == "image/jpeg"
        assert metadata["ContentLength"] == 2048
        assert metadata["ETag"] == '"abc123"'

    def test_get_file_metadata_not_found(
        self, storage_service: StorageService, mock_s3: MagicMock
    ) -> None:
        """Test getting metadata of non-existent file."""
        mock_s3.head_object.side_effect = ClientError(
            {"Error": {"Code": "404", "Message": "Not found"}}, "head_object"
        )

        with pytest.raises(StorageError, match="File not found"):
            storage_service.get_file_metadata("missing.jpg")


class TestStorageError:
    """Tests for StorageError exception."""

    def test_storage_error_message(self) -> None:
        """Test StorageError with message."""
        error = StorageError("Test error message")
        assert str(error) == "Test error message"

    def test_storage_error_inheritance(self) -> None:
        """Test StorageError inherits from Exception."""
        assert issubclass(StorageError, Exception)
