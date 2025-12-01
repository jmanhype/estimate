"""Tests for main FastAPI application."""

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client() -> TestClient:
    """Create test client."""
    return TestClient(app)


def test_root_endpoint(client: TestClient) -> None:
    """Test root endpoint returns API info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "EstiMate API"
    assert data["version"] == "1.0.0"
    assert data["docs"] == "/docs"


def test_health_endpoint(client: TestClient) -> None:
    """Test health endpoint returns healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_cors_middleware(client: TestClient) -> None:
    """Test CORS middleware is configured."""
    # Test CORS headers by making an OPTIONS request
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    # CORS middleware should add Access-Control-Allow-Origin header
    assert "access-control-allow-origin" in response.headers
