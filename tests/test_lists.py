from app.schemas.todo_list import TodoListCreate, TodoListOut


def test_todo_list_create_schema():
    data = TodoListCreate(name="Work", description="Work tasks")
    assert data.name == "Work"
    assert data.description == "Work tasks"


def test_todo_list_create_requires_name():
    import pytest
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        TodoListCreate()


def test_todo_list_out_schema():
    from datetime import datetime
    data = TodoListOut(id=1, name="Work", description=None, created_at=datetime.utcnow())
    assert data.id == 1
    assert data.name == "Work"
