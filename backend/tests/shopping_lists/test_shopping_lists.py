"""Tests for the ShoppingList module: create, read, update, delete,
plus item management (from pool or free text) and cascade delete."""

from tests.conftest import create_test_shopping_list, create_test_ingredient


class TestCreateShoppingList:
    """Happy path for POST /shopping-lists."""

    def test_create_shopping_list(self, client):
        data = create_test_shopping_list(client, name="Spesa settimana 1")
        assert data["name"] == "Spesa settimana 1"
        assert data["items"] == []
        assert "id" in data


class TestReadShoppingList:
    """GET /shopping-lists and GET /shopping-lists/{id}."""

    def test_get_shopping_list_by_id(self, client, sample_shopping_list):
        response = client.get(f"/shopping-lists/{sample_shopping_list['id']}")
        assert response.status_code == 200
        assert response.json()["name"] == "Lista test"

    def test_get_nonexistent_shopping_list_returns_404(self, client):
        response = client.get("/shopping-lists/9999")
        assert response.status_code == 404

    def test_get_all_shopping_lists(self, client, sample_shopping_list):
        response = client.get("/shopping-lists/")
        assert response.status_code == 200
        assert len(response.json()) == 1


class TestUpdateShoppingList:
    """PATCH /shopping-lists/{id}."""

    def test_update_shopping_list_name(self, client, sample_shopping_list):
        response = client.patch(
            f"/shopping-lists/{sample_shopping_list['id']}",
            json={"name": "Lista rinominata"},
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Lista rinominata"

    def test_update_nonexistent_shopping_list_returns_404(self, client):
        response = client.patch("/shopping-lists/9999", json={"name": "Test"})
        assert response.status_code == 404


class TestAddItemToShoppingList:
    """POST /shopping-lists/{id}/items -- both pool-linked and free-text items."""

    def test_add_item_from_pool(self, client, sample_shopping_list, sample_ingredient):
        response = client.post(
            f"/shopping-lists/{sample_shopping_list['id']}/items",
            json={
                "ingredient_id": sample_ingredient["id"],
                "quantity": 2,
                "unit": "pz",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_ingredient["name"]
        assert data["shopping_category"] == sample_ingredient["shopping_category"]
        assert data["ingredient_id"] == sample_ingredient["id"]

    def test_add_free_text_item(self, client, sample_shopping_list):
        response = client.post(
            f"/shopping-lists/{sample_shopping_list['id']}/items",
            json={"name": "Detersivo", "shopping_category": "Altro"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Detersivo"
        assert data["ingredient_id"] is None

    def test_add_item_without_ingredient_or_freetext_returns_422(
        self, client, sample_shopping_list
    ):
        response = client.post(
            f"/shopping-lists/{sample_shopping_list['id']}/items",
            json={"quantity": 1},
        )
        assert response.status_code == 422

    def test_add_item_with_nonexistent_ingredient_returns_404(
        self, client, sample_shopping_list
    ):
        response = client.post(
            f"/shopping-lists/{sample_shopping_list['id']}/items",
            json={"ingredient_id": 9999},
        )
        assert response.status_code == 404

    def test_add_item_to_nonexistent_list_returns_404(self, client, sample_ingredient):
        response = client.post(
            "/shopping-lists/9999/items",
            json={"ingredient_id": sample_ingredient["id"]},
        )
        assert response.status_code == 404


class TestUpdateShoppingListItem:
    """PATCH /shopping-lists/{list_id}/items/{item_id}."""

    def test_update_item_quantity(
        self, client, sample_shopping_list, sample_ingredient
    ):
        item = client.post(
            f"/shopping-lists/{sample_shopping_list['id']}/items",
            json={"ingredient_id": sample_ingredient["id"], "quantity": 1},
        ).json()

        response = client.patch(
            f"/shopping-lists/{sample_shopping_list['id']}/items/{item['id']}",
            json={"quantity": 5, "is_checked": True},
        )
        assert response.status_code == 200
        assert response.json()["quantity"] == 5
        assert response.json()["is_checked"] is True

    def test_update_item_on_wrong_list_returns_404(
        self, client, sample_shopping_list, sample_ingredient
    ):
        other_list = create_test_shopping_list(client, name="Altra lista")
        item = client.post(
            f"/shopping-lists/{sample_shopping_list['id']}/items",
            json={"ingredient_id": sample_ingredient["id"]},
        ).json()

        # Try to update the item using the wrong list_id in the URL
        response = client.patch(
            f"/shopping-lists/{other_list['id']}/items/{item['id']}",
            json={"quantity": 5},
        )
        assert response.status_code == 404


class TestDeleteShoppingListItem:
    """DELETE /shopping-lists/{list_id}/items/{item_id}."""

    def test_delete_item(self, client, sample_shopping_list, sample_ingredient):
        item = client.post(
            f"/shopping-lists/{sample_shopping_list['id']}/items",
            json={"ingredient_id": sample_ingredient["id"]},
        ).json()

        response = client.delete(
            f"/shopping-lists/{sample_shopping_list['id']}/items/{item['id']}"
        )
        assert response.status_code == 200

        list_response = client.get(f"/shopping-lists/{sample_shopping_list['id']}")
        assert list_response.json()["items"] == []

    def test_delete_nonexistent_item_returns_404(self, client, sample_shopping_list):
        response = client.delete(
            f"/shopping-lists/{sample_shopping_list['id']}/items/9999"
        )
        assert response.status_code == 404


class TestDeleteShoppingList:
    """DELETE /shopping-lists/{id} -- hard delete with cascade."""

    def test_delete_shopping_list_cascades_to_items(
        self, client, sample_shopping_list, sample_ingredient
    ):
        client.post(
            f"/shopping-lists/{sample_shopping_list['id']}/items",
            json={"ingredient_id": sample_ingredient["id"]},
        )

        response = client.delete(f"/shopping-lists/{sample_shopping_list['id']}")
        assert response.status_code == 200

        get_response = client.get(f"/shopping-lists/{sample_shopping_list['id']}")
        assert get_response.status_code == 404

    def test_delete_nonexistent_shopping_list_returns_404(self, client):
        response = client.delete("/shopping-lists/9999")
        assert response.status_code == 404
