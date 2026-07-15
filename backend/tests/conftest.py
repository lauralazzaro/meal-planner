import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db
from app.core.route_names import RouteName

TEST_DATABASE_URL = os.environ["TEST_DATABASE_URL"]

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

API_PREFIX = "/api/v1"


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


# --- Auth helpers ---


def register_and_login(client, email="test@test.com", password="password123"):
    """Register a new user and log in, returning the auth headers.

    Uses reverse routing (app.url_path_for) so these helpers stay correct even
    if the auth route paths are renamed on the router.
    """
    client.post(
        app.url_path_for(RouteName.AUTH_REGISTER),
        json={"email": email, "password": password},
    )
    response = client.post(
        app.url_path_for(RouteName.AUTH_LOGIN),
        data={"username": email, "password": password},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers(client):
    """Provide auth headers for the default test user."""
    return register_and_login(client)


@pytest.fixture
def other_user_headers(client):
    """Provide auth headers for a second, different user -- used to test
    that data isolation between users actually works."""
    return register_and_login(client, email="other@test.com")


# --- Ingredient helpers ---


def create_test_ingredient(client, headers, name="Pomodoro", category="vegetables"):
    """Helper to create an ingredient and return its data."""
    response = client.post(
        f"{API_PREFIX}/ingredients/",
        json={"name": name, "shopping_category": category},
        headers=headers,
    )
    return response.json()


@pytest.fixture
def sample_ingredient(client, auth_headers):
    """Create a sample ingredient owned by the default test user."""
    return create_test_ingredient(client, auth_headers)


# --- Dish helpers ---


def create_test_dish(client, headers, ingredient_id, label="Pasta al pomodoro"):
    """Helper to create a dish linked to an existing ingredient."""
    response = client.post(
        f"{API_PREFIX}/dishes/",
        json={"label": label, "main_ingredient_id": ingredient_id},
        headers=headers,
    )
    return response.json()


@pytest.fixture
def sample_dish(client, auth_headers, sample_ingredient):
    """Create a sample dish owned by the default test user."""
    return create_test_dish(client, auth_headers, sample_ingredient["id"])


# --- WeeklyPlan helpers ---


def create_test_weekly_plan(client, headers, name="Settimana test", is_default=False):
    """Helper to create a weekly plan."""
    response = client.post(
        f"{API_PREFIX}/weekly-plans/",
        json={"name": name, "is_default": is_default},
        headers=headers,
    )
    return response.json()


@pytest.fixture
def sample_weekly_plan(client, auth_headers):
    """Create a sample weekly plan owned by the default test user."""
    return create_test_weekly_plan(client, auth_headers)


# --- ShoppingList helpers ---


def create_test_shopping_list(client, headers, name="Lista test"):
    """Helper to create a shopping list."""
    response = client.post(
        f"{API_PREFIX}/shopping-lists/", json={"name": name}, headers=headers
    )
    return response.json()


@pytest.fixture
def sample_shopping_list(client, auth_headers):
    """Create a sample shopping list owned by the default test user."""
    return create_test_shopping_list(client, auth_headers)
