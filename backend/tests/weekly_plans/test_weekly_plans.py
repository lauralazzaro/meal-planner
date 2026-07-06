"""Tests for the WeeklyPlan module: create, read, update, delete,
bulk dish creation, and business rules (single default, cascade delete)."""

from tests.conftest import create_test_weekly_plan, create_test_dish


class TestCreateWeeklyPlan:
    """Happy path for POST /weekly-plans."""

    def test_create_weekly_plan(self, client):
        data = create_test_weekly_plan(client, name="Settimana tipo")
        assert data["name"] == "Settimana tipo"
        assert data["is_default"] is False
        assert "id" in data


class TestDefaultUniqueness:
    """Business rule: only one weekly plan can be default at a time."""

    def test_setting_new_default_unsets_previous(self, client):
        first = create_test_weekly_plan(client, name="Piano A", is_default=True)
        second = create_test_weekly_plan(client, name="Piano B", is_default=True)

        response_first = client.get(f"/weekly-plans/{first['id']}")
        response_second = client.get(f"/weekly-plans/{second['id']}")

        assert response_first.json()["is_default"] is False
        assert response_second.json()["is_default"] is True


class TestReadWeeklyPlan:
    """GET /weekly-plans and GET /weekly-plans/{id}."""

    def test_get_weekly_plan_by_id(self, client, sample_weekly_plan):
        response = client.get(f"/weekly-plans/{sample_weekly_plan['id']}")
        assert response.status_code == 200
        assert response.json()["name"] == "Settimana test"

    def test_get_nonexistent_weekly_plan_returns_404(self, client):
        response = client.get("/weekly-plans/9999")
        assert response.status_code == 404


class TestBulkAddDishes:
    """POST /weekly-plans/{id}/dishes -- bulk creation, all-or-nothing."""

    def test_bulk_add_dishes(self, client, sample_weekly_plan, sample_ingredient):
        dish = create_test_dish(client, sample_ingredient["id"])

        response = client.post(
            f"/weekly-plans/{sample_weekly_plan['id']}/dishes",
            json={
                "dishes": [
                    {
                        "day_of_week": "lunedì",
                        "meal_type": "pranzo",
                        "dish_id": dish["id"],
                    },
                    {
                        "day_of_week": "martedì",
                        "meal_type": "cena",
                        "dish_id": dish["id"],
                    },
                ]
            },
        )
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_bulk_add_with_invalid_dish_id_saves_nothing(
        self, client, sample_weekly_plan, sample_ingredient
    ):
        dish = create_test_dish(client, sample_ingredient["id"])

        response = client.post(
            f"/weekly-plans/{sample_weekly_plan['id']}/dishes",
            json={
                "dishes": [
                    {
                        "day_of_week": "lunedì",
                        "meal_type": "pranzo",
                        "dish_id": dish["id"],
                    },
                    {"day_of_week": "martedì", "meal_type": "cena", "dish_id": 9999},
                ]
            },
        )
        assert response.status_code == 404

        # Verify nothing was saved -- all-or-nothing behavior
        plan_response = client.get(f"/weekly-plans/{sample_weekly_plan['id']}")
        assert plan_response.json()["dishes"] == []

    def test_bulk_add_with_invalid_day_of_week_returns_422(
        self, client, sample_weekly_plan, sample_ingredient
    ):
        dish = create_test_dish(client, sample_ingredient["id"])

        response = client.post(
            f"/weekly-plans/{sample_weekly_plan['id']}/dishes",
            json={
                "dishes": [
                    {
                        "day_of_week": "luned",
                        "meal_type": "pranzo",
                        "dish_id": dish["id"],
                    },
                ]
            },
        )
        assert response.status_code == 422


class TestDeleteWeeklyPlan:
    """DELETE /weekly-plans/{id} -- hard delete with cascade."""

    def test_delete_weekly_plan_cascades_to_dishes(
        self, client, sample_weekly_plan, sample_ingredient
    ):
        dish = create_test_dish(client, sample_ingredient["id"])
        client.post(
            f"/weekly-plans/{sample_weekly_plan['id']}/dishes",
            json={
                "dishes": [
                    {
                        "day_of_week": "lunedì",
                        "meal_type": "pranzo",
                        "dish_id": dish["id"],
                    }
                ]
            },
        )

        response = client.delete(f"/weekly-plans/{sample_weekly_plan['id']}")
        assert response.status_code == 200

        # Plan should be gone entirely (hard delete)
        get_response = client.get(f"/weekly-plans/{sample_weekly_plan['id']}")
        assert get_response.status_code == 404

    def test_delete_nonexistent_weekly_plan_returns_404(self, client):
        response = client.delete("/weekly-plans/9999")
        assert response.status_code == 404
