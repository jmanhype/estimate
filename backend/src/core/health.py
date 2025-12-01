"""Health check module for API monitoring."""


def get_health_status() -> dict[str, str]:
    """
    Get the current health status of the application.

    Returns:
        dict: Health status with service name and status
    """
    return {"service": "estimate-backend", "status": "healthy"}
