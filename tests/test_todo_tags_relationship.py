"""
Task 2.2 — Add tags relationship to Todo model
RED phase: test runs before relationship is added; must fail.
"""
import pytest
from sqlalchemy import inspect

# Import all models so SQLAlchemy can resolve inter-model string references
# (e.g. Todo.list -> "TodoList") before inspecting relationships.
import app.models.todo_list  # noqa: F401


def test_todo_has_tags_attribute():
    """Todo must have a 'tags' attribute (relationship)."""
    from app.models.todo import Todo
    assert hasattr(Todo, "tags"), "Todo model must have a 'tags' attribute"


def test_todo_tags_is_relationship():
    """Todo.tags must be a SQLAlchemy relationship (not a plain column)."""
    from app.models.todo import Todo
    mapper = inspect(Todo)
    rel_names = {rel.key for rel in mapper.relationships}
    assert "tags" in rel_names, (
        f"'tags' must be a relationship on Todo; found relationships: {rel_names}"
    )


def test_todo_tags_uses_secondary_table():
    """Todo.tags relationship must use the todo_tags association table as secondary."""
    from app.models.todo import Todo
    from app.models.tag import todo_tags
    mapper = inspect(Todo)
    tags_rel = mapper.relationships["tags"]
    assert tags_rel.secondary is todo_tags, (
        "Todo.tags relationship must use todo_tags as secondary table"
    )


def test_todo_tags_selectin_loading():
    """Todo.tags relationship must use lazy='selectin' loading strategy."""
    from app.models.todo import Todo
    mapper = inspect(Todo)
    tags_rel = mapper.relationships["tags"]
    assert tags_rel.lazy == "selectin", (
        f"Todo.tags must use lazy='selectin'; got lazy='{tags_rel.lazy}'"
    )
