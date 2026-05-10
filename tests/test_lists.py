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


import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from main import app

TEST_DB_URL = "sqlite:///./test_integration.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def test_create_and_get_list(client):
    response = client.post("/lists", json={"name": "Work", "description": "Work tasks"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Work"
    assert "id" in data

    response = client.get("/lists")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_delete_list(client):
    response = client.post("/lists", json={"name": "Temp"})
    list_id = response.json()["id"]
    response = client.delete(f"/lists/{list_id}")
    assert response.status_code == 204
    response = client.get(f"/lists/{list_id}")
    assert response.status_code == 404
