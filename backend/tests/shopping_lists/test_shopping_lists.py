"""Tests for the ShoppingList module: create, read, update, delete,
item management (pool or free text), cascade delete, and multi-tenant isolation."""

from tests.conftest import create_test_shopping_list, API_PREFIX

ENDPOINT_SHOPPING_LIST = f"{API_PREFIX}/shopping-lists/"


class TestCreateShoppingList:
    def test_create_shopping_list(self, client, auth_headers):
        data = create_test_shopping_list(client, auth_headers, name="Spesa settimana 1")
        assert data["name"] == "Spesa settimana 1"
        assert data["items"] == []

    def test_create_shopping_list_without_auth_returns_401(self, client):
        response = client.post(ENDPOINT_SHOPPING_LIST, json={"name": "Test"})
        assert response.status_code == 401


class TestReadShoppingList:
    def test_get_shopping_list_by_id(self, client, auth_headers, sample_shopping_list):
        response = client.get(
            f"{ENDPOINT_SHOPPING_LIST}{sample_shopping_list['id']}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Lista test"

    def test_get_nonexistent_shopping_list_returns_404(self, client, auth_headers):
        response = client.get(f"{ENDPOINT_SHOPPING_LIST}9999", headers=auth_headers)
        assert response.status_code == 404

    def test_get_all_shopping_lists(self, client, auth_headers, sample_shopping_list):
        response = client.get(ENDPOINT_SHOPPING_LIST, headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_cannot_read_other_users_shopping_list(
        self, client, other_user_headers, sample_shopping_list
    ):
        response = client.get(
            f"{ENDPOINT_SHOPPING_LIST}{sample_shopping_list['id']}",
            headers=other_user_headers,
        )
        assert response.status_code == 404


class TestUpdateShoppingList:
    def test_update_shopping_list_name(
        self, client, auth_headers, sample_shopping_list
    ):
        response = client.patch(
            f"{ENDPOINT_SHOPPING_LIST}{sample_shopping_list['id']}",
            json={"name": "Lista rinominata"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Lista rinominata"

    def test_update_nonexistent_shopping_list_returns_404(self, client, auth_headers):
        response = client.patch(
            "/shopping-lists/9999", json={"name": "Test"}, headers=auth_headers
        )
        assert response.status_code == 404


class TestAddItemToShoppingList:
    def test_add_item_from_pool(
        self, client, auth_headers, sample_shopping_list, sample_ingredient
    ):
        response = client.post(
            f"{ENDPOINT_SHOPPING_LIST}{sample_shopping_list['id']}/items",
            json={
                "ingredient_id": sample_ingredient["id"],
                "quantity": 2,
                "unit": "pz",
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_ingredient["name"]
        assert data["ingredient_id"] == sample_ingredient["id"]

    def test_add_free_text_item(self, client, auth_headers, sample_shopping_list):
        response = client.post(
            f"{ENDPOINT_SHOPPING_LIST}{sample_shopping_list['id']}/items",
            json={"name": "Detersivo", "shopping_category": "Altro"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["ingredient_id"] is None

    def test_add_item_without_ingredient_or_freetext_returns_422(
        self, client, auth_headers, sample_shopping_list
    ):
        response = client.post(
            f"{ENDPOINT_SHOPPING_LIST}{sample_shopping_list['id']}/items",
            json={"quantity": 1},
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_add_item_with_nonexistent_ingredient_returns_404(
        self, client, auth_headers, sample_shopping_list
    ):
        response = client.post(
            f"{ENDPOINT_SHOPPING_LIST}{sample_shopping_list['id']}/items",
            json={"ingredient_id": 9999},
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_cannot_add_other_users_ingredient_to_list(
        self,
        client,
        auth_headers,
        other_user_headers,
        sample_shopping_list,
        sample_ingredient,
    ):
        """A user should not be able to add another user's ingredient to their list."""
        response = client.post(
            f"{ENDPOINT_SHOPPING_LIST}{sample_shopping_list['id']}/items",
            json={"ingredient_id": sample_ingredient["id"]},
            headers=other_user_headers,
        )
        assert response.status_code == 404


class TestUpdateShoppingListItem:
    def test_update_item_quantity(
        self, client, auth_headers, sample_shopping_list, sample_ingredient
    ):
        item = client.post(
            f"{ENDPOINT_SHOPPING_LIST}{sample_shopping_list['id']}/items",
            json={"ingredient_id": sample_ingredient["id"], "quantity": 1},
            headers=auth_headers,
        ).json()

        response = client.patch(
            f"{ENDPOINT_SHOPPING_LIST}{sample_shopping_list['id']}/items/{item['id']}",
            json={"quantity": 5, "is_checked": True},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["quantity"] == 5

    def test_cannot_update_item_on_other_users_list(
        self,
        client,
        auth_headers,
        other_user_headers,
        sample_shopping_list,
        sample_ingredient,
    ):
        item = client.post(
            f"{ENDPOINT_SHOPPING_LIST}{sample_shopping_list['id']}/items",
            json={"ingredient_id": sample_ingredient["id"]},
            headers=auth_headers,
        ).json()

        response = client.patch(
            f"{ENDPOINT_SHOPPING_LIST}{sample_shopping_list['id']}/items/{item['id']}",
            json={"quantity": 5},
            headers=other_user_headers,
        )
        assert response.status_code == 404


class TestDeleteShoppingListItem:
    def test_delete_item(
        self, client, auth_headers, sample_shopping_list, sample_ingredient
    ):
        item = client.post(
            f"{ENDPOINT_SHOPPING_LIST}{sample_shopping_list['id']}/items",
            json={"ingredient_id": sample_ingredient["id"]},
            headers=auth_headers,
        ).json()

        response = client.delete(
            f"{ENDPOINT_SHOPPING_LIST}{sample_shopping_list['id']}/items/{item['id']}",
            headers=auth_headers,
        )
        assert response.status_code == 200

    def test_delete_nonexistent_item_returns_404(
        self, client, auth_headers, sample_shopping_list
    ):
        response = client.delete(
            f"{ENDPOINT_SHOPPING_LIST}{sample_shopping_list['id']}/items/9999",
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestDeleteShoppingList:
    def test_delete_shopping_list_cascades_to_items(
        self, client, auth_headers, sample_shopping_list, sample_ingredient
    ):
        client.post(
            f"{ENDPOINT_SHOPPING_LIST}{sample_shopping_list['id']}/items",
            json={"ingredient_id": sample_ingredient["id"]},
            headers=auth_headers,
        )

        response = client.delete(
            f"{ENDPOINT_SHOPPING_LIST}{sample_shopping_list['id']}",
            headers=auth_headers,
        )
        assert response.status_code == 200

        get_response = client.get(
            f"{ENDPOINT_SHOPPING_LIST}{sample_shopping_list['id']}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404

    def test_delete_nonexistent_shopping_list_returns_404(self, client, auth_headers):
        response = client.delete("/shopping-lists/9999", headers=auth_headers)
        assert response.status_code == 404

    def test_cannot_delete_other_users_shopping_list(
        self, client, other_user_headers, sample_shopping_list
    ):
        response = client.delete(
            f"{ENDPOINT_SHOPPING_LIST}{sample_shopping_list['id']}",
            headers=other_user_headers,
        )
        assert response.status_code == 404
