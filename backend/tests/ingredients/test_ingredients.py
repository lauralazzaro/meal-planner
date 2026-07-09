"""Tests for the Ingredient module: create, read, update, delete,
validation, uniqueness constraint, and multi-tenant isolation."""

from tests.conftest import create_test_ingredient, register_and_login


class TestCreateIngredient:
    def test_create_ingredient(self, client, auth_headers):
        data = create_test_ingredient(client, auth_headers)
        assert data["name"] == "Pomodoro"
        assert "id" in data

    def test_create_ingredient_without_auth_returns_401(self, client):
        response = client.post(
            "/ingredients/",
            json={"name": "Pomodoro", "shopping_category": "vegetables"},
        )
        assert response.status_code == 401

    def test_create_duplicate_ingredient_returns_409(self, client, auth_headers):
        create_test_ingredient(client, auth_headers, name="Pomodoro")
        response = client.post(
            "/ingredients/",
            json={"name": "Pomodoro", "shopping_category": "vegetables"},
            headers=auth_headers,
        )
        assert response.status_code == 409

    def test_same_name_allowed_for_different_users(
        self, client, auth_headers, other_user_headers
    ):
        """The same ingredient name should be allowed across different users."""
        create_test_ingredient(client, auth_headers, name="Pomodoro")
        response = client.post(
            "/ingredients/",
            json={"name": "Pomodoro", "shopping_category": "vegetables"},
            headers=other_user_headers,
        )
        assert response.status_code == 200

    def test_create_with_empty_name_returns_422(self, client, auth_headers):
        response = client.post(
            "/ingredients/",
            json={"name": "", "shopping_category": "vegetables"},
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_create_with_name_over_max_length_returns_422(self, client, auth_headers):
        response = client.post(
            "/ingredients/",
            json={"name": "a" * 101, "shopping_category": "vegetables"},
            headers=auth_headers,
        )
        assert response.status_code == 422


class TestReadIngredient:
    def test_get_ingredient_by_id(self, client, auth_headers, sample_ingredient):
        response = client.get(
            f"/ingredients/{sample_ingredient['id']}", headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Pomodoro"

    def test_get_nonexistent_ingredient_returns_404(self, client, auth_headers):
        response = client.get("/ingredients/9999", headers=auth_headers)
        assert response.status_code == 404

    def test_get_all_ingredients(self, client, auth_headers, sample_ingredient):
        response = client.get("/ingredients/", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_cannot_read_other_users_ingredient(
        self, client, auth_headers, other_user_headers, sample_ingredient
    ):
        """A user should not be able to fetch another user's ingredient by id."""
        response = client.get(
            f"/ingredients/{sample_ingredient['id']}", headers=other_user_headers
        )
        assert response.status_code == 404

    def test_ingredient_list_isolated_between_users(
        self, client, auth_headers, other_user_headers, sample_ingredient
    ):
        """A user's ingredient list should not include another user's ingredients."""
        response = client.get("/ingredients/", headers=other_user_headers)
        assert response.json() == []


class TestUpdateIngredient:
    def test_update_ingredient_name(self, client, auth_headers, sample_ingredient):
        response = client.patch(
            f"/ingredients/{sample_ingredient['id']}",
            json={"name": "Pomodoro San Marzano"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Pomodoro San Marzano"

    def test_update_nonexistent_ingredient_returns_404(self, client, auth_headers):
        response = client.patch(
            "/ingredients/9999", json={"name": "Test"}, headers=auth_headers
        )
        assert response.status_code == 404

    def test_cannot_update_other_users_ingredient(
        self, client, auth_headers, other_user_headers, sample_ingredient
    ):
        response = client.patch(
            f"/ingredients/{sample_ingredient['id']}",
            json={"name": "Hacked"},
            headers=other_user_headers,
        )
        assert response.status_code == 404


class TestDeleteIngredient:
    def test_delete_ingredient(self, client, auth_headers, sample_ingredient):
        response = client.delete(
            f"/ingredients/{sample_ingredient['id']}", headers=auth_headers
        )
        assert response.status_code == 200

    def test_deleted_ingredient_not_in_list(
        self, client, auth_headers, sample_ingredient
    ):
        client.delete(f"/ingredients/{sample_ingredient['id']}", headers=auth_headers)
        response = client.get("/ingredients/", headers=auth_headers)
        assert sample_ingredient["id"] not in [i["id"] for i in response.json()]

    def test_delete_nonexistent_ingredient_returns_404(self, client, auth_headers):
        response = client.delete("/ingredients/9999", headers=auth_headers)
        assert response.status_code == 404

    def test_cannot_delete_other_users_ingredient(
        self, client, auth_headers, other_user_headers, sample_ingredient
    ):
        response = client.delete(
            f"/ingredients/{sample_ingredient['id']}", headers=other_user_headers
        )
        assert response.status_code == 404
