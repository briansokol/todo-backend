"""
Task 3.2 — Tags router integration tests
RED phase: all four stub endpoints return 501; these tests expect real behavior and FAIL.
GREEN phase: replace stubs with real implementations; all tests PASS.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from main import app

TEST_DB_URL = "sqlite:///./test_tags_router.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    def override():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override
    yield TestClient(app)
    app.dependency_overrides.clear()


# ── helpers ───────────────────────────────────────────────────────────────────

def _create_list(client):
    """Create a TodoList and return its id."""
    r = client.post("/lists", json={"name": "Test List"})
    assert r.status_code == 201
    return r.json()["id"]


def _create_todo(client, list_id):
    """Create a Todo in the given list and return its id."""
    r = client.post(f"/lists/{list_id}/todos", json={"title": "Test Todo"})
    assert r.status_code == 201
    return r.json()["id"]


def _create_tag(client, name="urgent", color="#ff0000"):
    """Create a Tag via POST /tags and return the full JSON response."""
    r = client.post("/tags", json={"name": name, "color": color})
    assert r.status_code == 201
    return r.json()


# ── GET /tags ─────────────────────────────────────────────────────────────────

def test_list_tags_returns_200_empty(client):
    """GET /tags returns 200 with an empty list when no tags exist."""
    r = client.get("/tags")
    assert r.status_code == 200
    assert r.json() == []


def test_list_tags_returns_all_created_tags(client):
    """GET /tags returns all created tags."""
    _create_tag(client, name="work", color="#0000ff")
    _create_tag(client, name="home", color="#00ff00")

    r = client.get("/tags")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 2
    names = {t["name"] for t in data}
    assert names == {"work", "home"}


def test_list_tags_response_shape(client):
    """Each tag in GET /tags response has id, name, and color fields."""
    _create_tag(client, name="shape-test", color="#abcdef")

    r = client.get("/tags")
    assert r.status_code == 200
    tag = r.json()[0]
    assert "id" in tag
    assert "name" in tag
    assert "color" in tag
    assert tag["name"] == "shape-test"
    assert tag["color"] == "#abcdef"


# ── POST /tags ────────────────────────────────────────────────────────────────

def test_create_tag_returns_201(client):
    """POST /tags returns 201 with the created tag."""
    r = client.post("/tags", json={"name": "urgent", "color": "#ff0000"})
    assert r.status_code == 201
    data = r.json()
    assert data["id"] is not None
    assert data["name"] == "urgent"
    assert data["color"] == "#ff0000"


def test_create_tag_persists(client):
    """Tag created via POST /tags is returned by subsequent GET /tags."""
    _create_tag(client, name="persist-me", color="#112233")

    r = client.get("/tags")
    assert r.status_code == 200
    names = [t["name"] for t in r.json()]
    assert "persist-me" in names


def test_create_tag_duplicate_returns_409(client):
    """POST /tags returns 409 when a tag with the same name already exists."""
    _create_tag(client, name="dup", color="#aabbcc")
    r = client.post("/tags", json={"name": "dup", "color": "#112233"})
    assert r.status_code == 409


def test_create_tag_invalid_color_returns_422(client):
    """POST /tags returns 422 when color is not a valid hex color."""
    r = client.post("/tags", json={"name": "bad-color", "color": "not-a-color"})
    assert r.status_code == 422


def test_create_tag_missing_color_returns_422(client):
    """POST /tags returns 422 when color field is absent."""
    r = client.post("/tags", json={"name": "x"})
    assert r.status_code == 422


def test_create_tag_empty_name_returns_422(client):
    """POST /tags returns 422 when name is empty."""
    r = client.post("/tags", json={"name": "", "color": "#ff0000"})
    assert r.status_code == 422


# ── POST /todos/{todo_id}/tags/{tag_id} ───────────────────────────────────────

def test_add_tag_to_todo_returns_204(client):
    """POST /todos/{todo_id}/tags/{tag_id} returns 204 on success."""
    list_id = _create_list(client)
    todo_id = _create_todo(client, list_id)
    tag = _create_tag(client)

    r = client.post(f"/todos/{todo_id}/tags/{tag['id']}")
    assert r.status_code == 204


def test_add_tag_to_todo_no_body(client):
    """POST /todos/{todo_id}/tags/{tag_id} returns no body on success."""
    list_id = _create_list(client)
    todo_id = _create_todo(client, list_id)
    tag = _create_tag(client)

    r = client.post(f"/todos/{todo_id}/tags/{tag['id']}")
    assert r.status_code == 204
    assert r.content == b""


def test_add_tag_to_todo_invalid_todo_returns_404(client):
    """POST /todos/{todo_id}/tags/{tag_id} returns 404 when todo does not exist."""
    tag = _create_tag(client)
    r = client.post(f"/todos/99999/tags/{tag['id']}")
    assert r.status_code == 404


def test_add_tag_to_todo_invalid_tag_returns_404(client):
    """POST /todos/{todo_id}/tags/{tag_id} returns 404 when tag does not exist."""
    list_id = _create_list(client)
    todo_id = _create_todo(client, list_id)
    r = client.post(f"/todos/{todo_id}/tags/99999")
    assert r.status_code == 404


def test_add_tag_to_todo_tag_visible_on_todo(client):
    """After adding, tag appears in the todo's tags array on GET /todos/{id}."""
    list_id = _create_list(client)
    todo_id = _create_todo(client, list_id)
    tag = _create_tag(client, name="visible", color="#cccccc")

    client.post(f"/todos/{todo_id}/tags/{tag['id']}")

    r = client.get(f"/todos/{todo_id}")
    assert r.status_code == 200
    tag_ids = [t["id"] for t in r.json()["tags"]]
    assert tag["id"] in tag_ids


def test_add_tag_visible_in_list_todos(client):
    """After adding, tag appears in the todo's tags array on GET /lists/{list_id}/todos."""
    list_id = _create_list(client)
    todo_id = _create_todo(client, list_id)
    tag = _create_tag(client, name="list-visible", color="#aabbcc")

    client.post(f"/todos/{todo_id}/tags/{tag['id']}")

    r = client.get(f"/lists/{list_id}/todos")
    assert r.status_code == 200
    todos = r.json()
    assert len(todos) == 1
    tag_ids = [t["id"] for t in todos[0]["tags"]]
    assert tag["id"] in tag_ids


# ── DELETE /todos/{todo_id}/tags/{tag_id} ─────────────────────────────────────

def test_remove_tag_from_todo_returns_204(client):
    """DELETE /todos/{todo_id}/tags/{tag_id} returns 204 on success."""
    list_id = _create_list(client)
    todo_id = _create_todo(client, list_id)
    tag = _create_tag(client)

    client.post(f"/todos/{todo_id}/tags/{tag['id']}")
    r = client.delete(f"/todos/{todo_id}/tags/{tag['id']}")
    assert r.status_code == 204


def test_remove_tag_from_todo_no_body(client):
    """DELETE /todos/{todo_id}/tags/{tag_id} returns no body on success."""
    list_id = _create_list(client)
    todo_id = _create_todo(client, list_id)
    tag = _create_tag(client)

    client.post(f"/todos/{todo_id}/tags/{tag['id']}")
    r = client.delete(f"/todos/{todo_id}/tags/{tag['id']}")
    assert r.status_code == 204
    assert r.content == b""


def test_remove_tag_from_todo_invalid_todo_returns_404(client):
    """DELETE /todos/{todo_id}/tags/{tag_id} returns 404 when todo does not exist."""
    tag = _create_tag(client)
    r = client.delete(f"/todos/99999/tags/{tag['id']}")
    assert r.status_code == 404


def test_remove_tag_from_todo_invalid_tag_returns_404(client):
    """DELETE /todos/{todo_id}/tags/{tag_id} returns 404 when tag does not exist."""
    list_id = _create_list(client)
    todo_id = _create_todo(client, list_id)
    r = client.delete(f"/todos/{todo_id}/tags/99999")
    assert r.status_code == 404


def test_remove_tag_from_todo_tag_absent_from_todo(client):
    """After removing, tag no longer appears in the todo's tags array."""
    list_id = _create_list(client)
    todo_id = _create_todo(client, list_id)
    tag = _create_tag(client, name="removable", color="#dddddd")

    client.post(f"/todos/{todo_id}/tags/{tag['id']}")
    client.delete(f"/todos/{todo_id}/tags/{tag['id']}")

    r = client.get(f"/todos/{todo_id}")
    assert r.status_code == 200
    tag_ids = [t["id"] for t in r.json()["tags"]]
    assert tag["id"] not in tag_ids
