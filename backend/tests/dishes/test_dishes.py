"""Tests for the Dish module: create, read, update, delete,
validation, and multi-tenant isolation."""

from tests.conftest import create_test_dish, API_PREFIX

ENDPOINT_DISHES = f"{API_PREFIX}/dishes/"


class TestCreateDish:
    def test_create_dish(self, client, auth_headers, sample_ingredient):
        data = create_test_dish(client, auth_headers, sample_ingredient["id"])
        assert data["label"] == "Pasta al pomodoro"
        assert data["main_ingredient"]["name"] == "Pomodoro"

    def test_create_dish_without_auth_returns_401(self, client, sample_ingredient):
        response = client.post(
            ENDPOINT_DISHES,
            json={"label": "Test", "main_ingredient_id": sample_ingredient["id"]},
        )
        assert response.status_code == 401

    def test_create_dish_with_nonexistent_ingredient_returns_404(
        self, client, auth_headers
    ):
        response = client.post(
            ENDPOINT_DISHES,
            json={"label": "Piatto impossibile", "main_ingredient_id": 9999},
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_cannot_create_dish_with_other_users_ingredient(
        self, client, auth_headers, other_user_headers, sample_ingredient
    ):
        """A user should not be able to create a dish linked to another user's ingredient."""
        response = client.post(
            ENDPOINT_DISHES,
            json={
                "label": "Piatto rubato",
                "main_ingredient_id": sample_ingredient["id"],
            },
            headers=other_user_headers,
        )
        assert response.status_code == 404

    def test_create_dish_without_main_ingredient_returns_422(
        self, client, auth_headers
    ):
        response = client.post(
            ENDPOINT_DISHES, json={"label": "Test"}, headers=auth_headers
        )
        assert response.status_code == 422


class TestReadDish:
    def test_get_dish_by_id(self, client, auth_headers, sample_dish):
        response = client.get(
            f"{ENDPOINT_DISHES}{sample_dish['id']}", headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["label"] == "Pasta al pomodoro"

    def test_get_nonexistent_dish_returns_404(self, client, auth_headers):
        response = client.get(f"{ENDPOINT_DISHES}9999", headers=auth_headers)
        assert response.status_code == 404

    def test_get_all_dishes(self, client, auth_headers, sample_dish):
        response = client.get(ENDPOINT_DISHES, headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_cannot_read_other_users_dish(
        self, client, auth_headers, other_user_headers, sample_dish
    ):
        response = client.get(
            f"{ENDPOINT_DISHES}{sample_dish['id']}", headers=other_user_headers
        )
        assert response.status_code == 404

    def test_dish_list_isolated_between_users(
        self, client, other_user_headers, sample_dish
    ):
        response = client.get(ENDPOINT_DISHES, headers=other_user_headers)
        assert response.json() == []


class TestUpdateDish:
    def test_update_dish_label(self, client, auth_headers, sample_dish):
        response = client.patch(
            f"{ENDPOINT_DISHES}{sample_dish['id']}",
            json={"label": "Nuovo nome"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["label"] == "Nuovo nome"

    def test_update_nonexistent_dish_returns_404(self, client, auth_headers):
        response = client.patch(
            f"{ENDPOINT_DISHES}9999", json={"label": "Test"}, headers=auth_headers
        )
        assert response.status_code == 404

    def test_cannot_update_other_users_dish(
        self, client, other_user_headers, sample_dish
    ):
        response = client.patch(
            f"{ENDPOINT_DISHES}{sample_dish['id']}",
            json={"label": "Hacked"},
            headers=other_user_headers,
        )
        assert response.status_code == 404


class TestDeleteDish:
    def test_delete_dish(self, client, auth_headers, sample_dish):
        response = client.delete(
            f"{ENDPOINT_DISHES}{sample_dish['id']}", headers=auth_headers
        )
        assert response.status_code == 200

    def test_deleted_dish_not_in_list(self, client, auth_headers, sample_dish):
        client.delete(f"{ENDPOINT_DISHES}{sample_dish['id']}", headers=auth_headers)
        response = client.get(ENDPOINT_DISHES, headers=auth_headers)
        assert sample_dish["id"] not in [d["id"] for d in response.json()]

    def test_delete_nonexistent_dish_returns_404(self, client, auth_headers):
        response = client.delete(f"{ENDPOINT_DISHES}9999", headers=auth_headers)
        assert response.status_code == 404

    def test_cannot_delete_other_users_dish(
        self, client, other_user_headers, sample_dish
    ):
        response = client.delete(
            f"{ENDPOINT_DISHES}{sample_dish['id']}", headers=other_user_headers
        )
        assert response.status_code == 404
