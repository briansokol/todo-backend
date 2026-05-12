"""
Task 2.1 — Tag model and association table
RED phase: test runs before tag.py exists; must fail with ImportError.
"""
import pytest
from sqlalchemy import Table, inspect


def test_tag_model_importable():
    """Tag and todo_tags must be importable from app.models.tag."""
    from app.models.tag import Tag, todo_tags  # noqa: F401


def test_todo_tags_is_table():
    """todo_tags must be a SQLAlchemy Table construct."""
    from app.models.tag import todo_tags
    assert isinstance(todo_tags, Table)


def test_todo_tags_columns():
    """todo_tags must have todo_id and tag_id columns."""
    from app.models.tag import todo_tags
    col_names = {col.name for col in todo_tags.columns}
    assert "todo_id" in col_names
    assert "tag_id" in col_names


def test_todo_tags_primary_keys():
    """Both columns of todo_tags must be part of the composite primary key."""
    from app.models.tag import todo_tags
    pk_cols = {col.name for col in todo_tags.primary_key}
    assert pk_cols == {"todo_id", "tag_id"}


def test_todo_tags_cascade_delete():
    """Both FK columns must have ondelete=CASCADE."""
    from app.models.tag import todo_tags
    for col in todo_tags.columns:
        for fk in col.foreign_keys:
            assert fk.ondelete.upper() == "CASCADE", (
                f"Column {col.name} FK missing ondelete=CASCADE"
            )


def test_tag_tablename():
    """Tag.__tablename__ must be 'tags'."""
    from app.models.tag import Tag
    assert Tag.__tablename__ == "tags"


def test_tag_has_id_column():
    """Tag must have an 'id' primary key column."""
    from app.models.tag import Tag
    mapper = inspect(Tag)
    col = mapper.columns["id"]
    assert col.primary_key


def test_tag_has_name_column():
    """Tag must have a 'name' column: String(50), unique, not nullable."""
    from app.models.tag import Tag
    mapper = inspect(Tag)
    col = mapper.columns["name"]
    assert col.type.length == 50
    assert col.unique
    assert not col.nullable


def test_tag_has_color_column():
    """Tag must have a 'color' column: String(7), not nullable."""
    from app.models.tag import Tag
    mapper = inspect(Tag)
    col = mapper.columns["color"]
    assert col.type.length == 7
    assert not col.nullable


def test_tag_fields_match_tagout_schema():
    """Tag fields must match TagOut Pydantic schema (id, name, color)."""
    from app.models.tag import Tag
    from app.schemas.todo import TagOut
    required_fields = set(TagOut.model_fields.keys())  # id, name, color
    mapper = inspect(Tag)
    model_columns = set(mapper.columns.keys())
    assert required_fields.issubset(model_columns), (
        f"Tag model missing fields required by TagOut: "
        f"{required_fields - model_columns}"
    )
