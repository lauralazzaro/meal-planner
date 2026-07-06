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


def create_test_ingredient(client, name="Pomodoro", category="vegetables"):
    """Helper to create an ingredient and return its data."""

    response = client.post(
        "/ingredients/",
        json={"name": name, "shopping_category": category},
    )
    return response.json()


@pytest.fixture
def sample_ingredient(client):
    """Create a sample ingredient and return its data."""

    return create_test_ingredient(client)


def create_test_dish(client, ingredient_id, label="Pasta al pomodoro"):
    """Helper to create a dish linked to an existing ingredient."""

    response = client.post(
        "/dishes/",
        json={"label": label, "main_ingredient_id": ingredient_id},
    )
    return response.json()


@pytest.fixture
def sample_dish(client, sample_ingredient):
    """Create a sample dish linked to sample_ingredient."""

    return create_test_dish(client, sample_ingredient["id"])


def create_test_weekly_plan(client, name="Settimana test", is_default=False):
    """Helper to create a weekly plan."""

    response = client.post(
        "/weekly-plans/",
        json={"name": name, "is_default": is_default},
    )
    return response.json()


@pytest.fixture
def sample_weekly_plan(client):
    """Create a sample weekly plan."""

    return create_test_weekly_plan(client)
