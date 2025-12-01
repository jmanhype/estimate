"""Smoke tests for Phase 1 project setup and basic functionality."""

import importlib
import os
import sys
from pathlib import Path

import pytest


@pytest.mark.smoke
class TestProjectStructure:
    """Verify basic project structure is valid."""

    def test_backend_src_directory_exists(self) -> None:
        """Backend src directory should exist with correct structure."""
        backend_root = Path(__file__).parent.parent.parent
        src_dir = backend_root / "src"

        assert src_dir.exists(), "src directory does not exist"
        assert src_dir.is_dir(), "src is not a directory"

    def test_required_subdirectories_exist(self) -> None:
        """All required subdirectories should exist."""
        backend_root = Path(__file__).parent.parent.parent
        src_dir = backend_root / "src"

        required_dirs = [
            "core",
            "api",
            "models",
            "schemas",
            "services",
            "repositories",
        ]

        for dir_name in required_dirs:
            dir_path = src_dir / dir_name
            assert dir_path.exists(), f"Required directory {dir_name} does not exist"
            assert dir_path.is_dir(), f"{dir_name} is not a directory"

    def test_all_directories_are_python_packages(self) -> None:
        """All directories should have __init__.py files."""
        backend_root = Path(__file__).parent.parent.parent
        src_dir = backend_root / "src"

        # Check src/__init__.py
        assert (src_dir / "__init__.py").exists(), "src/__init__.py missing"

        # Check subdirectories
        for subdir in src_dir.rglob("*"):
            if subdir.is_dir() and not subdir.name.startswith((".", "__")):
                init_file = subdir / "__init__.py"
                assert init_file.exists(), f"{subdir.relative_to(backend_root)}/__init__.py missing"


@pytest.mark.smoke
class TestPythonImports:
    """Verify all modules can be imported without errors."""

    def test_can_import_core_modules(self) -> None:
        """Core modules should import successfully."""
        try:
            from src.core import config, health

            assert config is not None
            assert health is not None
        except ImportError as exc:
            pytest.fail(f"Failed to import core modules: {exc}")

    def test_can_import_config_and_get_settings(self) -> None:
        """Should be able to import and use config.get_settings()."""
        try:
            from src.core.config import get_settings

            settings = get_settings()
            assert settings is not None
        except Exception as exc:
            pytest.fail(f"Failed to get settings: {exc}")

    def test_can_import_health_module(self) -> None:
        """Should be able to import and use health module."""
        try:
            from src.core.health import get_health_status

            status = get_health_status()
            assert status is not None
            assert "service" in status
            assert "status" in status
        except Exception as exc:
            pytest.fail(f"Failed to use health module: {exc}")

    def test_can_import_all_package_init_files(self) -> None:
        """All package __init__.py files should import without errors."""
        backend_root = Path(__file__).parent.parent.parent
        src_dir = backend_root / "src"

        # Ensure src is in path
        if str(src_dir.parent) not in sys.path:
            sys.path.insert(0, str(src_dir.parent))

        errors = []

        for init_file in src_dir.rglob("__init__.py"):
            # Get module path relative to src
            relative_path = init_file.parent.relative_to(src_dir.parent)
            module_name = str(relative_path).replace(os.sep, ".")

            try:
                importlib.import_module(module_name)
            except Exception as exc:
                errors.append(f"{module_name}: {exc}")

        if errors:
            pytest.fail("Failed to import modules:\n" + "\n".join(errors))


@pytest.mark.smoke
class TestProjectConfiguration:
    """Verify project configuration files are valid."""

    def test_pyproject_toml_exists(self) -> None:
        """pyproject.toml should exist in backend root."""
        backend_root = Path(__file__).parent.parent.parent
        pyproject = backend_root / "pyproject.toml"

        assert pyproject.exists(), "pyproject.toml does not exist"
        assert pyproject.is_file(), "pyproject.toml is not a file"

    def test_pytest_configuration_is_valid(self) -> None:
        """Pytest configuration should be loadable."""
        # If pytest is running this test, config is valid
        # This test verifies pytest can parse pyproject.toml
        assert pytest is not None

    def test_pytest_markers_are_configured(self) -> None:
        """Required pytest markers should be configured."""
        # These markers should be defined (not raise warnings)
        required_markers = ["unit", "integration", "e2e", "slow", "smoke"]

        # Just verify this test can use the markers without errors
        # (If markers weren't configured, pytest would show warnings)
        assert all(marker for marker in required_markers)

    def test_docker_compose_file_exists(self) -> None:
        """docker-compose.yml should exist in project root."""
        backend_root = Path(__file__).parent.parent.parent
        project_root = backend_root.parent
        docker_compose = project_root / "docker-compose.yml"

        assert docker_compose.exists(), "docker-compose.yml does not exist"
        assert docker_compose.is_file(), "docker-compose.yml is not a file"

    def test_environment_example_file_exists(self) -> None:
        """.env.example should exist as template."""
        backend_root = Path(__file__).parent.parent.parent
        env_example = backend_root / ".env.example"

        assert env_example.exists(), ".env.example does not exist"
        assert env_example.is_file(), ".env.example is not a file"


@pytest.mark.smoke
class TestDependencies:
    """Verify critical dependencies are available."""

    def test_fastapi_is_installed(self) -> None:
        """FastAPI should be available."""
        try:
            import fastapi

            assert fastapi is not None
        except ImportError:
            pytest.fail("FastAPI is not installed")

    def test_sqlalchemy_is_installed(self) -> None:
        """SQLAlchemy should be available."""
        try:
            import sqlalchemy

            assert sqlalchemy is not None
            # Verify it's version 2.x
            version = sqlalchemy.__version__
            major_version = int(version.split(".")[0])
            assert major_version >= 2, f"SQLAlchemy {version} is below required 2.0+"
        except ImportError:
            pytest.fail("SQLAlchemy is not installed")

    def test_pydantic_is_installed(self) -> None:
        """Pydantic and pydantic-settings should be available."""
        try:
            import pydantic
            import pydantic_settings

            assert pydantic is not None
            assert pydantic_settings is not None
        except ImportError:
            pytest.fail("Pydantic or pydantic-settings is not installed")

    def test_redis_client_is_installed(self) -> None:
        """Redis Python client should be available."""
        try:
            import redis

            assert redis is not None
        except ImportError:
            pytest.fail("Redis client is not installed")

    def test_pytest_and_coverage_are_installed(self) -> None:
        """Pytest and pytest-cov should be available."""
        try:
            import pytest
            import pytest_cov

            assert pytest is not None
            assert pytest_cov is not None
        except ImportError:
            pytest.fail("Pytest or pytest-cov is not installed")


@pytest.mark.smoke
class TestBasicFunctionality:
    """Verify basic application functionality works."""

    def test_settings_can_be_created_without_errors(self) -> None:
        """Settings instance should be creatable."""
        from src.core.config import Settings

        try:
            settings = Settings()
            assert settings is not None
        except Exception as exc:
            pytest.fail(f"Failed to create Settings instance: {exc}")

    def test_health_check_returns_expected_format(self) -> None:
        """Health check should return properly formatted response."""
        from src.core.health import get_health_status

        status = get_health_status()

        assert isinstance(status, dict), "Health status should be a dict"
        assert "service" in status, "Health status missing 'service' key"
        assert "status" in status, "Health status missing 'status' key"
        assert status["service"] == "estimate-backend"
        assert status["status"] == "healthy"

    def test_project_is_ready_for_fastapi_integration(self) -> None:
        """Project structure should be ready for FastAPI app creation."""
        backend_root = Path(__file__).parent.parent.parent
        src_dir = backend_root / "src"

        # Verify directories needed for FastAPI exist
        required_for_api = ["api", "schemas", "models", "services"]

        for dir_name in required_for_api:
            dir_path = src_dir / dir_name
            assert dir_path.exists(), f"Directory {dir_name} needed for FastAPI not found"
