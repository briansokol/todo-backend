"""
Task 2.3 — Alembic migration for tags and todo_tags tables.
RED phase: test runs before migration exists; must fail with FileNotFoundError
or assertion errors.
"""
import ast
import os
import re
import glob
import pytest


VERSIONS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "alembic", "versions"
)


def _find_add_tags_migration():
    """Find the migration file that adds tags (not the initial schema)."""
    pattern = os.path.join(VERSIONS_DIR, "*.py")
    files = sorted(glob.glob(pattern))
    for path in files:
        basename = os.path.basename(path)
        if basename.startswith("96539a736435"):
            continue  # skip initial migration
        return path
    return None


def test_add_tags_migration_file_exists():
    """A second migration file must exist in alembic/versions/ (not initial)."""
    path = _find_add_tags_migration()
    assert path is not None, (
        "No add_tags migration file found in alembic/versions/. "
        "Expected a file other than 96539a736435_initial_schema.py."
    )


def test_migration_has_correct_down_revision():
    """Migration must chain from the initial schema revision."""
    path = _find_add_tags_migration()
    assert path is not None, "Migration file missing"
    source = open(path).read()
    assert "96539a736435" in source, (
        "down_revision must reference '96539a736435' (the initial schema)"
    )


def test_migration_creates_tags_table():
    """upgrade() must create the 'tags' table."""
    path = _find_add_tags_migration()
    assert path is not None, "Migration file missing"
    source = open(path).read()
    assert "create_table" in source, "upgrade() must call op.create_table"
    assert "'tags'" in source or '"tags"' in source, (
        "upgrade() must create a table named 'tags'"
    )


def test_migration_creates_todo_tags_table():
    """upgrade() must create the 'todo_tags' association table."""
    path = _find_add_tags_migration()
    assert path is not None, "Migration file missing"
    source = open(path).read()
    assert "'todo_tags'" in source or '"todo_tags"' in source, (
        "upgrade() must create a table named 'todo_tags'"
    )


def test_migration_tags_has_name_column():
    """tags table must include a 'name' column definition."""
    path = _find_add_tags_migration()
    assert path is not None, "Migration file missing"
    source = open(path).read()
    assert "'name'" in source or '"name"' in source, (
        "tags table definition must include a 'name' column"
    )


def test_migration_tags_has_color_column():
    """tags table must include a 'color' column definition."""
    path = _find_add_tags_migration()
    assert path is not None, "Migration file missing"
    source = open(path).read()
    assert "'color'" in source or '"color"' in source, (
        "tags table definition must include a 'color' column"
    )


def test_migration_todo_tags_has_todo_id_column():
    """todo_tags table must include a 'todo_id' FK column."""
    path = _find_add_tags_migration()
    assert path is not None, "Migration file missing"
    source = open(path).read()
    assert "'todo_id'" in source or '"todo_id"' in source, (
        "todo_tags table must include a 'todo_id' FK column"
    )


def test_migration_todo_tags_has_tag_id_column():
    """todo_tags table must include a 'tag_id' FK column."""
    path = _find_add_tags_migration()
    assert path is not None, "Migration file missing"
    source = open(path).read()
    assert "'tag_id'" in source or '"tag_id"' in source, (
        "todo_tags table must include a 'tag_id' FK column"
    )


def test_migration_has_downgrade():
    """Migration must define a downgrade() that drops the tables."""
    path = _find_add_tags_migration()
    assert path is not None, "Migration file missing"
    source = open(path).read()
    assert "def downgrade" in source, "Migration must define downgrade()"
    assert "drop_table" in source, "downgrade() must call op.drop_table"


def test_migration_does_not_alter_existing_tables():
    """Migration must NOT alter todo_lists or todos tables."""
    path = _find_add_tags_migration()
    assert path is not None, "Migration file missing"
    source = open(path).read()
    # Only allowed create_table calls are 'tags' and 'todo_tags'
    create_table_calls = re.findall(r"op\.create_table\(['\"](\w+)['\"]", source)
    for table in create_table_calls:
        assert table in ("tags", "todo_tags"), (
            f"Migration creates unexpected table '{table}'; "
            "must only create 'tags' and 'todo_tags'"
        )
    # No alter_table calls allowed
    assert "op.alter_table" not in source and "alter_column" not in source, (
        "Migration must not alter existing tables"
    )


def test_migration_imports_cleanly():
    """Migration file must be valid Python (parseable by ast)."""
    path = _find_add_tags_migration()
    assert path is not None, "Migration file missing"
    source = open(path).read()
    try:
        ast.parse(source)
    except SyntaxError as exc:
        pytest.fail(f"Migration file has a syntax error: {exc}")
