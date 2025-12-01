"""Integration tests for Alembic database migrations."""

import importlib.util
import inspect
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory


@pytest.fixture
def alembic_config():
    """Get Alembic configuration."""
    config_path = Path(__file__).parent.parent.parent / "alembic.ini"
    config = Config(str(config_path))
    # Override database URL to use test database or skip if not available
    return config


@pytest.fixture
def script_directory(alembic_config):
    """Get Alembic script directory."""
    return ScriptDirectory.from_config(alembic_config)


class TestMigrationFiles:
    """Test migration file structure and syntax."""

    def test_all_migrations_have_docstrings(self, script_directory):
        """Test that all migration files have docstrings."""
        migrations_dir = Path(script_directory.dir) / "versions"
        migration_files = list(migrations_dir.glob("*.py"))

        assert len(migration_files) > 0, "No migration files found"

        for migration_file in migration_files:
            if migration_file.name == "__init__.py":
                continue

            # Load module
            spec = importlib.util.spec_from_file_location("migration", migration_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Check docstring
            assert module.__doc__ is not None, f"{migration_file.name} missing docstring"
            assert len(module.__doc__.strip()) > 0, f"{migration_file.name} has empty docstring"

    def test_all_migrations_have_upgrade_downgrade(self, script_directory):
        """Test that all migrations have upgrade() and downgrade() functions."""
        migrations_dir = Path(script_directory.dir) / "versions"
        migration_files = list(migrations_dir.glob("*.py"))

        assert len(migration_files) > 0, "No migration files found"

        for migration_file in migration_files:
            if migration_file.name == "__init__.py":
                continue

            # Load module
            spec = importlib.util.spec_from_file_location("migration", migration_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Check for upgrade function
            assert hasattr(module, "upgrade"), f"{migration_file.name} missing upgrade() function"
            assert callable(module.upgrade), f"{migration_file.name} upgrade is not callable"

            # Check for downgrade function
            assert hasattr(
                module, "downgrade"
            ), f"{migration_file.name} missing downgrade() function"
            assert callable(module.downgrade), f"{migration_file.name} downgrade is not callable"

    def test_migrations_have_required_attributes(self, script_directory):
        """Test that all migrations have required revision attributes."""
        migrations_dir = Path(script_directory.dir) / "versions"
        migration_files = list(migrations_dir.glob("*.py"))

        assert len(migration_files) > 0, "No migration files found"

        for migration_file in migration_files:
            if migration_file.name == "__init__.py":
                continue

            # Load module
            spec = importlib.util.spec_from_file_location("migration", migration_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Check required attributes
            assert hasattr(module, "revision"), f"{migration_file.name} missing revision"
            assert isinstance(module.revision, str), f"{migration_file.name} revision must be string"

            assert hasattr(module, "down_revision"), f"{migration_file.name} missing down_revision"
            # down_revision can be None for the first migration

    def test_upgrade_functions_not_empty(self, script_directory):
        """Test that upgrade functions actually do something."""
        migrations_dir = Path(script_directory.dir) / "versions"
        migration_files = list(migrations_dir.glob("*.py"))

        assert len(migration_files) > 0, "No migration files found"

        for migration_file in migration_files:
            if migration_file.name == "__init__.py":
                continue

            # Load module
            spec = importlib.util.spec_from_file_location("migration", migration_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Check that upgrade function has some operations
            source = inspect.getsource(module.upgrade)
            # Should have more than just "pass"
            lines = [line.strip() for line in source.split("\n") if line.strip()]
            # Filter out docstrings, comments, and function definition
            code_lines = [
                line
                for line in lines
                if not line.startswith("#")
                and not line.startswith('"""')
                and not line.startswith("'''")
                and not line.startswith("def ")
            ]

            assert len(code_lines) > 1, f"{migration_file.name} upgrade() appears to be empty"

    def test_downgrade_functions_not_empty(self, script_directory):
        """Test that downgrade functions actually do something."""
        migrations_dir = Path(script_directory.dir) / "versions"
        migration_files = list(migrations_dir.glob("*.py"))

        assert len(migration_files) > 0, "No migration files found"

        for migration_file in migration_files:
            if migration_file.name == "__init__.py":
                continue

            # Load module
            spec = importlib.util.spec_from_file_location("migration", migration_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Check that downgrade function has some operations
            source = inspect.getsource(module.downgrade)
            # Should have more than just "pass"
            lines = [line.strip() for line in source.split("\n") if line.strip()]
            # Filter out docstrings, comments, and function definition
            code_lines = [
                line
                for line in lines
                if not line.startswith("#")
                and not line.startswith('"""')
                and not line.startswith("'''")
                and not line.startswith("def ")
            ]

            assert len(code_lines) > 1, f"{migration_file.name} downgrade() appears to be empty"


class TestMigrationChain:
    """Test migration revision chain."""

    def test_migration_chain_is_linear(self, script_directory):
        """Test that migrations form a linear chain."""
        revisions = list(script_directory.walk_revisions())

        # Should have at least one migration
        assert len(revisions) > 0, "No migrations found"

        # Check that each revision (except the first) has exactly one down_revision
        for revision in revisions:
            if revision.down_revision is not None:
                # Should be a single string, not a tuple (which would indicate branching)
                assert isinstance(
                    revision.down_revision, (str, type(None))
                ), f"Migration {revision.revision} has multiple down_revisions (branching detected)"

    def test_migration_heads(self, script_directory):
        """Test that there is exactly one migration head."""
        heads = script_directory.get_heads()

        # Should have exactly one head (no branching)
        assert len(heads) == 1, f"Expected 1 migration head, found {len(heads)}: {heads}"

    def test_migration_revisions_unique(self, script_directory):
        """Test that all revision IDs are unique."""
        revisions = list(script_directory.walk_revisions())
        revision_ids = [rev.revision for rev in revisions]

        # Check for duplicates
        assert len(revision_ids) == len(
            set(revision_ids)
        ), f"Duplicate revision IDs found: {revision_ids}"


class TestMigrationContent:
    """Test migration content for common issues."""

    def test_migrations_use_proper_imports(self, script_directory):
        """Test that migrations import required modules."""
        migrations_dir = Path(script_directory.dir) / "versions"
        migration_files = list(migrations_dir.glob("*.py"))

        for migration_file in migration_files:
            if migration_file.name == "__init__.py":
                continue

            content = migration_file.read_text()

            # Should import op from alembic
            assert "from alembic import op" in content, f"{migration_file.name} missing alembic import"

            # Should import sqlalchemy
            assert (
                "import sqlalchemy" in content
            ), f"{migration_file.name} missing sqlalchemy import"

    def test_first_migration_has_no_down_revision(self, script_directory):
        """Test that the first migration has down_revision = None."""
        revisions = list(script_directory.walk_revisions())

        # Find the first migration (one with down_revision = None)
        first_migrations = [rev for rev in revisions if rev.down_revision is None]

        assert (
            len(first_migrations) == 1
        ), f"Expected exactly 1 first migration, found {len(first_migrations)}"

    def test_migrations_create_expected_tables(self, script_directory):
        """Test that migrations create expected tables."""
        migrations_dir = Path(script_directory.dir) / "versions"
        migration_files = list(migrations_dir.glob("*.py"))

        all_content = ""
        for migration_file in migration_files:
            if migration_file.name == "__init__.py":
                continue
            all_content += migration_file.read_text()

        # Expected tables from the schema
        expected_tables = [
            "user_profiles",
            "subscriptions",
            "projects",
            "project_photos",
            "project_phases",
            "project_feedback",
            "shopping_lists",
            "shopping_list_items",
            "retailer_prices",
        ]

        for table in expected_tables:
            assert (
                f"'{table}'" in all_content or f'"{table}"' in all_content
            ), f"Table {table} not found in any migration"
