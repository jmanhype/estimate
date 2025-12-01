"""Tests for health check module."""

from src.core.health import get_health_status


def test_get_health_status_returns_correct_structure() -> None:
    """Health status should return service name and status."""
    result = get_health_status()

    assert "service" in result
    assert "status" in result


def test_get_health_status_returns_healthy() -> None:
    """Health status should report healthy."""
    result = get_health_status()

    assert result["service"] == "estimate-backend"
    assert result["status"] == "healthy"
