"""Tests for the Ingredient module: create, read, update, delete,
plus validation and business rule checks (uniqueness constraint)."""

from tests.conftest import create_test_ingredient


class TestCreateIngredient:
    """Happy path and validation for POST /ingredients."""

    def test_create_ingredient(self, client):
        data = create_test_ingredient(client)
        assert data["name"] == "Pomodoro"
        assert "id" in data

    def test_create_duplicate_ingredient_returns_409(self, client):
        create_test_ingredient(client, name="Pomodoro")
        response = client.post(
            "/ingredients/",
            json={"name": "Pomodoro", "shopping_category": "vegetables"},
        )
        assert response.status_code == 409

    def test_create_with_empty_name_returns_422(self, client):
        response = client.post(
            "/ingredients/",
            json={"name": "", "shopping_category": "vegetables"},
        )
        assert response.status_code == 422

    def test_create_with_name_over_max_length_returns_422(self, client):
        response = client.post(
            "/ingredients/",
            json={"name": "a" * 101, "shopping_category": "vegetables"},
        )
        assert response.status_code == 422


class TestReadIngredient:
    """GET /ingredients and GET /ingredients/{id}."""

    def test_get_ingredient_by_id(self, client):
        created = create_test_ingredient(client)
        response = client.get(f"/ingredients/{created['id']}")
        assert response.status_code == 200
        assert response.json()["name"] == "Pomodoro"

    def test_get_nonexistent_ingredient_returns_404(self, client):
        response = client.get("/ingredients/9999")
        assert response.status_code == 404

    def test_get_all_ingredients(self, client):
        create_test_ingredient(client)
        response = client.get("/ingredients/")
        assert response.status_code == 200
        assert len(response.json()) == 1


class TestUpdateIngredient:
    """PATCH /ingredients/{id}."""

    def test_update_ingredient_name(self, client):
        created = create_test_ingredient(client)
        response = client.patch(
            f"/ingredients/{created['id']}", json={"name": "Pomodoro San Marzano"}
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Pomodoro San Marzano"

    def test_update_nonexistent_ingredient_returns_404(self, client):
        response = client.patch("/ingredients/9999", json={"name": "Test"})
        assert response.status_code == 404


class TestDeleteIngredient:
    """DELETE /ingredients/{id} (soft delete)."""

    def test_delete_ingredient(self, client):
        created = create_test_ingredient(client)
        response = client.delete(f"/ingredients/{created['id']}")
        assert response.status_code == 200

    def test_deleted_ingredient_not_in_list(self, client):
        created = create_test_ingredient(client)
        client.delete(f"/ingredients/{created['id']}")
        response = client.get("/ingredients/")
        assert created["id"] not in [i["id"] for i in response.json()]

    def test_delete_nonexistent_ingredient_returns_404(self, client):
        response = client.delete("/ingredients/9999")
        assert response.status_code == 404
