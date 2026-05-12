import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base

# Use in-memory SQLite to guarantee full isolation between test functions.
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def db():
    # Import all models so metadata is fully populated before create_all.
    import app.models.todo_list  # noqa: F401
    import app.models.todo       # noqa: F401
    import app.models.tag        # noqa: F401

    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    yield session
    session.close()
    engine.dispose()
