"""
Task 3.1 — Tag CRUD service functions
RED phase: app/services/tags.py does not exist yet; tests fail with ImportError.
GREEN phase: create the file with real implementations; all tests pass.
"""
import pytest
from fastapi import HTTPException

# Import all models so SQLAlchemy can resolve inter-model string references
# before Base.metadata.create_all() runs in the db fixture.
import app.models.todo_list  # noqa: F401
import app.models.todo       # noqa: F401
import app.models.tag        # noqa: F401


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_list(db):
    """Create a TodoList row and return it (needed to satisfy FK on Todo)."""
    from app.models.todo_list import TodoList
    todo_list = TodoList(name="Test List")
    db.add(todo_list)
    db.commit()
    db.refresh(todo_list)
    return todo_list


def _make_todo(db, list_id):
    """Create a Todo row and return it."""
    from app.models.todo import Todo
    todo = Todo(list_id=list_id, title="Test Todo")
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


def _make_tag(db, name="urgent", color="#ff0000"):
    """Create a Tag row directly and return it."""
    from app.models.tag import Tag
    tag = Tag(name=name, color=color)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


# ── get_tags ─────────────────────────────────────────────────────────────────

def test_get_tags_returns_empty_list(db):
    """get_tags returns an empty list when no tags exist."""
    from app.services.tags import get_tags
    result = get_tags(db)
    assert result == []


def test_get_tags_returns_all_tags(db):
    """get_tags returns all Tag rows."""
    from app.services.tags import get_tags
    _make_tag(db, name="work", color="#0000ff")
    _make_tag(db, name="home", color="#00ff00")
    result = get_tags(db)
    assert len(result) == 2
    names = {t.name for t in result}
    assert names == {"work", "home"}


# ── create_tag ───────────────────────────────────────────────────────────────

def test_create_tag_success(db):
    """create_tag persists a new tag and returns it with an id."""
    from app.services.tags import create_tag
    from app.schemas.todo import TagCreate
    data = TagCreate(name="urgent", color="#ff0000")
    tag = create_tag(db, data)
    assert tag.id is not None
    assert tag.name == "urgent"
    assert tag.color == "#ff0000"


def test_create_tag_persists_to_db(db):
    """Tag created by create_tag is queryable from the DB session."""
    from app.services.tags import create_tag, get_tags
    from app.schemas.todo import TagCreate
    create_tag(db, TagCreate(name="saved", color="#123456"))
    all_tags = get_tags(db)
    assert len(all_tags) == 1
    assert all_tags[0].name == "saved"


def test_create_tag_duplicate_name_raises_409(db):
    """create_tag raises HTTPException(409) when name already exists."""
    from app.services.tags import create_tag
    from app.schemas.todo import TagCreate
    create_tag(db, TagCreate(name="dup", color="#aabbcc"))
    with pytest.raises(HTTPException) as exc_info:
        create_tag(db, TagCreate(name="dup", color="#112233"))
    assert exc_info.value.status_code == 409
    assert "already exists" in exc_info.value.detail.lower()


# ── add_tag_to_todo ───────────────────────────────────────────────────────────

def test_add_tag_to_todo_success(db):
    """add_tag_to_todo links the tag to the todo; todo.tags includes the tag."""
    from app.services.tags import add_tag_to_todo
    todo_list = _make_list(db)
    todo = _make_todo(db, todo_list.id)
    tag = _make_tag(db)

    add_tag_to_todo(db, todo.id, tag.id)

    db.refresh(todo)
    assert len(todo.tags) == 1
    assert todo.tags[0].id == tag.id


def test_add_tag_to_todo_invalid_todo_raises_404(db):
    """add_tag_to_todo raises HTTPException(404) when todo_id does not exist."""
    from app.services.tags import add_tag_to_todo
    tag = _make_tag(db)
    with pytest.raises(HTTPException) as exc_info:
        add_tag_to_todo(db, todo_id=99999, tag_id=tag.id)
    assert exc_info.value.status_code == 404
    assert "todo" in exc_info.value.detail.lower()


def test_add_tag_to_todo_invalid_tag_raises_404(db):
    """add_tag_to_todo raises HTTPException(404) when tag_id does not exist."""
    from app.services.tags import add_tag_to_todo
    todo_list = _make_list(db)
    todo = _make_todo(db, todo_list.id)
    with pytest.raises(HTTPException) as exc_info:
        add_tag_to_todo(db, todo_id=todo.id, tag_id=99999)
    assert exc_info.value.status_code == 404
    assert "tag" in exc_info.value.detail.lower()


# ── remove_tag_from_todo ──────────────────────────────────────────────────────

def test_remove_tag_from_todo_success(db):
    """remove_tag_from_todo unlinks the tag; todo.tags no longer includes it."""
    from app.services.tags import add_tag_to_todo, remove_tag_from_todo
    todo_list = _make_list(db)
    todo = _make_todo(db, todo_list.id)
    tag = _make_tag(db)

    add_tag_to_todo(db, todo.id, tag.id)
    db.refresh(todo)
    assert len(todo.tags) == 1

    remove_tag_from_todo(db, todo.id, tag.id)
    db.refresh(todo)
    assert len(todo.tags) == 0


def test_remove_tag_from_todo_invalid_todo_raises_404(db):
    """remove_tag_from_todo raises HTTPException(404) when todo_id does not exist."""
    from app.services.tags import remove_tag_from_todo
    tag = _make_tag(db)
    with pytest.raises(HTTPException) as exc_info:
        remove_tag_from_todo(db, todo_id=99999, tag_id=tag.id)
    assert exc_info.value.status_code == 404
    assert "todo" in exc_info.value.detail.lower()


def test_remove_tag_from_todo_invalid_tag_raises_404(db):
    """remove_tag_from_todo raises HTTPException(404) when tag_id does not exist."""
    from app.services.tags import remove_tag_from_todo
    todo_list = _make_list(db)
    todo = _make_todo(db, todo_list.id)
    with pytest.raises(HTTPException) as exc_info:
        remove_tag_from_todo(db, todo_id=todo.id, tag_id=99999)
    assert exc_info.value.status_code == 404
    assert "tag" in exc_info.value.detail.lower()
