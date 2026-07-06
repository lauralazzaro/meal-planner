"""Tests for the Dish module: create, read, update, delete,
plus validation for the required main_ingredient_id."""

from tests.conftest import create_test_dish


class TestCreateDish:
    """Happy path and validation for POST /dishes."""

    def test_create_dish(self, client, sample_ingredient):
        data = create_test_dish(client, sample_ingredient["id"])
        assert data["label"] == "Pasta al pomodoro"
        assert data["main_ingredient"]["name"] == "Pomodoro"
        assert "id" in data

    def test_create_dish_with_nonexistent_ingredient_returns_404(self, client):
        response = client.post(
            "/dishes/",
            json={"label": "Piatto impossibile", "main_ingredient_id": 9999},
        )
        assert response.status_code == 404

    def test_create_dish_without_main_ingredient_returns_422(self, client):
        response = client.post(
            "/dishes/",
            json={"label": "Piatto senza ingrediente"},
        )
        assert response.status_code == 422

    def test_create_dish_with_label_over_max_length_returns_422(
        self, client, sample_ingredient
    ):
        response = client.post(
            "/dishes/",
            json={"label": "a" * 101, "main_ingredient_id": sample_ingredient["id"]},
        )
        assert response.status_code == 422


class TestReadDish:
    """GET /dishes and GET /dishes/{id}."""

    def test_get_dish_by_id(self, client, sample_dish):
        response = client.get(f"/dishes/{sample_dish['id']}")
        assert response.status_code == 200
        assert response.json()["label"] == "Pasta al pomodoro"

    def test_get_nonexistent_dish_returns_404(self, client):
        response = client.get("/dishes/9999")
        assert response.status_code == 404

    def test_get_all_dishes(self, client, sample_dish):
        response = client.get("/dishes/")
        assert response.status_code == 200
        assert len(response.json()) == 1


class TestUpdateDish:
    """PATCH /dishes/{id}."""

    def test_update_dish_label(self, client, sample_dish):
        response = client.patch(
            f"/dishes/{sample_dish['id']}", json={"label": "Pasta al pomodoro speciale"}
        )
        assert response.status_code == 200
        assert response.json()["label"] == "Pasta al pomodoro speciale"

    def test_update_nonexistent_dish_returns_404(self, client):
        response = client.patch("/dishes/9999", json={"label": "Test"})
        assert response.status_code == 404


class TestDeleteDish:
    """DELETE /dishes/{id} (soft delete)."""

    def test_delete_dish(self, client, sample_dish):
        response = client.delete(f"/dishes/{sample_dish['id']}")
        assert response.status_code == 200

    def test_deleted_dish_not_in_list(self, client, sample_dish):
        client.delete(f"/dishes/{sample_dish['id']}")
        response = client.get("/dishes/")
        assert sample_dish["id"] not in [d["id"] for d in response.json()]

    def test_delete_nonexistent_dish_returns_404(self, client):
        response = client.delete("/dishes/9999")
        assert response.status_code == 404
