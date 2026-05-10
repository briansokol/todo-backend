from app.schemas.todo import TodoCreate, TodoOut, TodoUpdate
from app.models.todo import Priority, Status
from datetime import datetime


def test_todo_create_defaults():
    data = TodoCreate(title="Buy milk")
    assert data.title == "Buy milk"
    assert data.priority == Priority.medium


def test_todo_create_requires_title():
    import pytest
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        TodoCreate()


def test_todo_out_has_tags_as_empty_list():
    data = TodoOut(
        id=1, list_id=1, title="Test", status=Status.pending,
        priority=Priority.medium, created_at=datetime.utcnow(), tags=[]
    )
    assert data.tags == []
