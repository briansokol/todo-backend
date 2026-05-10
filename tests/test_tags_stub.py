import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from main import app

TEST_DB_URL = "sqlite:///./test_tags.db"
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
    return TestClient(app)


def test_tags_list_returns_501(client):
    response = client.get("/tags")
    assert response.status_code == 501
    assert "not yet implemented" in response.json()["detail"].lower()


def test_tags_create_returns_501(client):
    response = client.post("/tags", json={"name": "urgent", "color": "#ff0000"})
    assert response.status_code == 501
    assert "not yet implemented" in response.json()["detail"].lower()
