import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db

TEST_DATABASE_URL = os.environ["TEST_DATABASE_URL"]

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Create all tables before each test, drop them after."""

    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Provide a TestClient for making requests in tests."""
    return TestClient(app)


@pytest.fixture
def sample_dish(client, sample_ingredient):
    """Create a sample dish linked to sample_ingredient and return its data."""
    response = client.post(
        "/dishes/",
        json={
            "label": "Pasta al pomodoro",
            "main_ingredient_id": sample_ingredient["id"],
        },
    )
    return response.json()


def create_test_ingredient(client, name="Pomodoro", category="vegetables"):
    """Helper to create an ingredient and return its data."""
    response = client.post(
        "/ingredients/",
        json={"name": name, "shopping_category": category},
    )
    return response.json()
