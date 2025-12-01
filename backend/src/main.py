"""EstiMate API - Main application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.core.health import get_health_status

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="EstiMate AI Materials Estimation API",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return get_health_status()


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "message": settings.api_title,
        "version": settings.api_version,
        "docs": "/docs",
    }
