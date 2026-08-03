"""Tests for the WeeklyPlan module: create, read, update, delete,
bulk dish creation, business rules, and multi-tenant isolation."""

import uuid

from tests.conftest import (
    create_test_weekly_plan,
    create_test_dish,
)
from app.main import app
from app.core.route_names import RouteName
from app.core.enums import DayOfWeek, MealType


class TestCreateWeeklyPlan:
    def test_create_weekly_plan(self, client, auth_headers):
        data = create_test_weekly_plan(client, auth_headers, name="Settimana tipo")
        assert data["name"] == "Settimana tipo"
        assert data["is_default"] is False

    def test_create_weekly_plan_without_auth_returns_401(self, client):
        response = client.post(
            app.url_path_for(RouteName.WEEKLY_PLAN_CREATE),
            json={"name": "Test", "is_default": False},
        )
        assert response.status_code == 401


class TestDefaultUniqueness:
    def test_setting_new_default_unsets_previous(self, client, auth_headers):
        first = create_test_weekly_plan(
            client, auth_headers, name="Piano A", is_default=True
        )
        second = create_test_weekly_plan(
            client, auth_headers, name="Piano B", is_default=True
        )

        response_first = client.get(
            app.url_path_for(RouteName.WEEKLY_PLAN_DETAIL, plan_id=first["id"]),
            headers=auth_headers,
        )
        response_second = client.get(
            app.url_path_for(RouteName.WEEKLY_PLAN_DETAIL, plan_id=second["id"]),
            headers=auth_headers,
        )

        assert response_first.json()["is_default"] is False
        assert response_second.json()["is_default"] is True

    def test_default_uniqueness_is_per_user(
        self, client, auth_headers, other_user_headers
    ):
        """Each user should be able to have their own default plan independently."""
        plan_a = create_test_weekly_plan(
            client, auth_headers, name="Piano A", is_default=True
        )
        plan_b = create_test_weekly_plan(
            client, other_user_headers, name="Piano B", is_default=True
        )

        response_a = client.get(
            app.url_path_for(RouteName.WEEKLY_PLAN_DETAIL, plan_id=plan_a["id"]),
            headers=auth_headers,
        )
        response_b = client.get(
            app.url_path_for(RouteName.WEEKLY_PLAN_DETAIL, plan_id=plan_b["id"]),
            headers=other_user_headers,
        )

        assert response_a.json()["is_default"] is True
        assert response_b.json()["is_default"] is True


class TestReadWeeklyPlan:
    def test_get_weekly_plan_by_id(self, client, auth_headers, sample_weekly_plan):
        response = client.get(
            app.url_path_for(
                RouteName.WEEKLY_PLAN_DETAIL, plan_id=sample_weekly_plan["id"]
            ),
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["name"] == "Settimana test"

    def test_get_nonexistent_weekly_plan_returns_404(self, client, auth_headers):
        response = client.get(
            app.url_path_for(RouteName.WEEKLY_PLAN_DETAIL, plan_id=str(uuid.uuid4())),
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_cannot_read_other_users_weekly_plan(
        self, client, other_user_headers, sample_weekly_plan
    ):
        response = client.get(
            app.url_path_for(
                RouteName.WEEKLY_PLAN_DETAIL, plan_id=sample_weekly_plan["id"]
            ),
            headers=other_user_headers,
        )
        assert response.status_code == 404


class TestBulkAddDishes:
    def test_bulk_add_dishes(
        self, client, auth_headers, sample_weekly_plan, sample_ingredient
    ):
        dish = create_test_dish(
            client, auth_headers, sample_ingredient["id"], "Risotto"
        )

        response = client.post(
            app.url_path_for(
                RouteName.WEEKLY_PLAN_ADD_DISHES,
                plan_id=sample_weekly_plan["id"],
            ),
            json={
                "dishes": [
                    {
                        "day_of_week": DayOfWeek.MONDAY,
                        "meal_type": MealType.LUNCH,
                        "dish_public_id": dish["id"],
                    },
                    {
                        "day_of_week": DayOfWeek.TUESDAY,
                        "meal_type": MealType.DINNER,
                        "dish_public_id": dish["id"],
                    },
                ]
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_bulk_add_with_invalid_dish_id_saves_nothing(
        self, client, auth_headers, sample_weekly_plan, sample_ingredient
    ):
        dish = create_test_dish(client, auth_headers, sample_ingredient["id"])

        response = client.post(
            app.url_path_for(
                RouteName.WEEKLY_PLAN_ADD_DISHES,
                plan_id=sample_weekly_plan["id"],
            ),
            json={
                "dishes": [
                    {
                        "day_of_week": DayOfWeek.MONDAY,
                        "meal_type": MealType.LUNCH,
                        "dish_public_id": dish["id"],
                    },
                    {
                        "day_of_week": DayOfWeek.TUESDAY,
                        "meal_type": MealType.DINNER,
                        "dish_public_id": str(uuid.uuid4()),
                    },
                ]
            },
            headers=auth_headers,
        )
        assert response.status_code == 404

        plan_response = client.get(
            app.url_path_for(
                RouteName.WEEKLY_PLAN_DETAIL, plan_id=sample_weekly_plan["id"]
            ),
            headers=auth_headers,
        )
        assert plan_response.json()["dishes"] == []

    def test_bulk_add_with_invalid_day_of_week_returns_422(
        self, client, auth_headers, sample_weekly_plan, sample_ingredient
    ):
        dish = create_test_dish(client, auth_headers, sample_ingredient["id"])

        response = client.post(
            app.url_path_for(
                RouteName.WEEKLY_PLAN_ADD_DISHES,
                plan_id=sample_weekly_plan["id"],
            ),
            json={
                "dishes": [
                    {
                        "day_of_week": "NOT_A_DAY",
                        "meal_type": "LUNCH",
                        "dish_public_id": dish["id"],
                    }
                ]
            },
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_cannot_bulk_add_using_other_users_dish(
        self,
        client,
        auth_headers,
        other_user_headers,
        sample_weekly_plan,
        sample_ingredient,
    ):
        """A user should not be able to add another user's dish to their own plan."""
        dish = create_test_dish(client, auth_headers, sample_ingredient["id"])

        other_plan = create_test_weekly_plan(
            client, other_user_headers, name="Piano altro utente"
        )
        response = client.post(
            app.url_path_for(
                RouteName.WEEKLY_PLAN_ADD_DISHES, plan_id=other_plan["id"]
            ),
            json={
                "dishes": [
                    {
                        "day_of_week": DayOfWeek.MONDAY,
                        "meal_type": MealType.DINNER,
                        "dish_public_id": dish["id"],
                    }
                ]
            },
            headers=other_user_headers,
        )
        assert response.status_code == 404


class TestDeleteWeeklyPlan:
    def test_delete_weekly_plan_cascades_to_dishes(
        self, client, auth_headers, sample_weekly_plan, sample_ingredient
    ):
        dish = create_test_dish(client, auth_headers, sample_ingredient["id"])
        client.post(
            app.url_path_for(
                RouteName.WEEKLY_PLAN_ADD_DISHES,
                plan_id=sample_weekly_plan["id"],
            ),
            json={
                "dishes": [
                    {
                        "day_of_week": "MONDAY",
                        "meal_type": "LUNCH",
                        "dish_public_id": dish["id"],
                    }
                ]
            },
            headers=auth_headers,
        )

        response = client.delete(
            app.url_path_for(
                RouteName.WEEKLY_PLAN_DELETE, plan_id=sample_weekly_plan["id"]
            ),
            headers=auth_headers,
        )
        assert response.status_code == 200

        get_response = client.get(
            app.url_path_for(
                RouteName.WEEKLY_PLAN_DETAIL, plan_id=sample_weekly_plan["id"]
            ),
            headers=auth_headers,
        )
        assert get_response.status_code == 404

    def test_delete_nonexistent_weekly_plan_returns_404(self, client, auth_headers):
        response = client.delete(
            app.url_path_for(RouteName.WEEKLY_PLAN_DELETE, plan_id=str(uuid.uuid4())),
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_cannot_delete_other_users_weekly_plan(
        self, client, other_user_headers, sample_weekly_plan
    ):
        response = client.delete(
            app.url_path_for(
                RouteName.WEEKLY_PLAN_DELETE, plan_id=sample_weekly_plan["id"]
            ),
            headers=other_user_headers,
        )
        assert response.status_code == 404
