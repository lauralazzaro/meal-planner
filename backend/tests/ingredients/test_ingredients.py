"""Tests for the Ingredient module: create, read, update, delete,
validation, uniqueness constraint, and multi-tenant isolation."""

import uuid

from tests.conftest import create_test_ingredient
from app.core.route_names import RouteName
from app.main import app


class TestCreateIngredient:
    def test_create_ingredient(self, client, auth_headers):
        data = create_test_ingredient(client, auth_headers)
        assert data["name"] == "Pomodoro"
        assert "id" in data

    def test_create_ingredient_without_auth_returns_401(self, client):
        response = client.post(
            app.url_path_for(RouteName.INGREDIENT_CREATE),
            json={"name": "Pomodoro", "shopping_category": "vegetables"},
        )
        assert response.status_code == 401

    def test_create_duplicate_ingredient_returns_409(self, client, auth_headers):
        create_test_ingredient(client, auth_headers, name="Pomodoro")
        response = client.post(
            app.url_path_for(RouteName.INGREDIENT_CREATE),
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
            app.url_path_for(RouteName.INGREDIENT_CREATE),
            json={"name": "Pomodoro", "shopping_category": "vegetables"},
            headers=other_user_headers,
        )
        assert response.status_code == 200

    def test_create_with_empty_name_returns_422(self, client, auth_headers):
        response = client.post(
            app.url_path_for(RouteName.INGREDIENT_CREATE),
            json={"name": "", "shopping_category": "vegetables"},
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_create_with_name_over_max_length_returns_422(self, client, auth_headers):
        response = client.post(
            app.url_path_for(RouteName.INGREDIENT_CREATE),
            json={"name": "a" * 101, "shopping_category": "vegetables"},
            headers=auth_headers,
        )
        assert response.status_code == 422


class TestReadIngredient:
    def test_get_ingredient_by_id(self, client, auth_headers, sample_ingredient):
        response = client.get(
            app.url_path_for(
                RouteName.INGREDIENT_DETAIL,
                ingredient_id=sample_ingredient["id"],
            ),
            headers=auth_headers,
        )
        assert response.status_code == 200

        assert response.json()["name"] == "Pomodoro"

    def test_get_nonexistent_ingredient_returns_404(self, client, auth_headers):
        response = client.get(
            app.url_path_for(
                RouteName.INGREDIENT_DETAIL, ingredient_id=str(uuid.uuid4())
            ),
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_get_all_ingredients(self, client, auth_headers, sample_ingredient):
        response = client.get(
            app.url_path_for(RouteName.INGREDIENT_LIST), headers=auth_headers
        )
        assert response.status_code == 200
        assert len(response.json()["items"]) == 1

    def test_cannot_read_other_users_ingredient(
        self, client, other_user_headers, sample_ingredient
    ):
        """A user should not be able to fetch another user's ingredient by id."""
        response = client.get(
            app.url_path_for(
                RouteName.INGREDIENT_DETAIL,
                ingredient_id=sample_ingredient["id"],
            ),
            headers=other_user_headers,
        )
        assert response.status_code == 404

    def test_ingredient_list_isolated_between_users(
        self,
        client,
        other_user_headers,
    ):
        """A user's ingredient list should not include another user's ingredients."""
        response = client.get(
            app.url_path_for(RouteName.INGREDIENT_LIST), headers=other_user_headers
        )

        assert response.json() == {
            "items": [],
            "next_cursor": None,
            "has_next": False,
        }

    def test_get_paginated_ingredients(
        self,
        client,
        auth_headers,
    ):
        """Get a paginated list of ingredients"""

        create_test_ingredient(client, auth_headers, name="Carota")
        create_test_ingredient(client, auth_headers, name="Aglio")
        create_test_ingredient(client, auth_headers, name="Basilico")

        response = client.get(
            app.url_path_for(RouteName.INGREDIENT_LIST),
            params={"limit": 2},
            headers=auth_headers,
        )

        data = response.json()
        names = [item["name"] for item in data["items"]]

        assert len(names) == 2
        assert names == ["Aglio", "Basilico"]
        assert response.json()["has_next"] is True

        response2 = client.get(
            app.url_path_for(RouteName.INGREDIENT_LIST),
            params={"after": data["next_cursor"]},
            headers=auth_headers,
        )

        data2 = response2.json()
        names2 = [item["name"] for item in data2["items"]]

        assert names2 == ["Carota"]
        assert data2["has_next"] is False


class TestUpdateIngredient:
    def test_update_ingredient_name(self, client, auth_headers, sample_ingredient):
        response = client.patch(
            app.url_path_for(
                RouteName.INGREDIENT_UPDATE,
                ingredient_id=sample_ingredient["id"],
            ),
            json={"name": "Pomodoro San Marzano"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Pomodoro San Marzano"

    def test_update_nonexistent_ingredient_returns_404(self, client, auth_headers):
        response = client.patch(
            app.url_path_for(
                RouteName.INGREDIENT_UPDATE, ingredient_id=str(uuid.uuid4())
            ),
            json={"name": "Test"},
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_cannot_update_other_users_ingredient(
        self, client, other_user_headers, sample_ingredient
    ):
        response = client.patch(
            app.url_path_for(
                RouteName.INGREDIENT_UPDATE,
                ingredient_id=sample_ingredient["id"],
            ),
            json={"name": "Hacked"},
            headers=other_user_headers,
        )
        assert response.status_code == 404


class TestDeleteIngredient:
    def test_delete_ingredient(self, client, auth_headers, sample_ingredient):
        response = client.delete(
            app.url_path_for(
                RouteName.INGREDIENT_DELETE,
                ingredient_id=sample_ingredient["id"],
            ),
            headers=auth_headers,
        )
        assert response.status_code == 200

    def test_deleted_ingredient_not_in_list(
        self, client, auth_headers, sample_ingredient
    ):
        client.delete(
            app.url_path_for(
                RouteName.INGREDIENT_DELETE,
                ingredient_id=sample_ingredient["id"],
            ),
            headers=auth_headers,
        )
        response = client.get(
            app.url_path_for(RouteName.INGREDIENT_LIST), headers=auth_headers
        )
        assert sample_ingredient["id"] not in [
            i["id"] for i in response.json()["items"]
        ]

    def test_delete_nonexistent_ingredient_returns_404(self, client, auth_headers):
        response = client.delete(
            app.url_path_for(
                RouteName.INGREDIENT_DELETE, ingredient_id=str(uuid.uuid4())
            ),
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_cannot_delete_other_users_ingredient(
        self, client, other_user_headers, sample_ingredient
    ):
        response = client.delete(
            app.url_path_for(
                RouteName.INGREDIENT_DELETE,
                ingredient_id=sample_ingredient["id"],
            ),
            headers=other_user_headers,
        )
        assert response.status_code == 404


class TestPaginationEdgeCases:
    def test_limit_over_max_returns_422(self, client, auth_headers):
        response = client.get(
            app.url_path_for(RouteName.INGREDIENT_LIST),
            params={"limit": 101},
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_limit_below_min_returns_422(self, client, auth_headers):
        response = client.get(
            app.url_path_for(RouteName.INGREDIENT_LIST),
            params={"limit": 0},
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_malformed_cursor_returns_400(self, client, auth_headers):
        response = client.get(
            app.url_path_for(RouteName.INGREDIENT_LIST),
            params={"after": "not-valid-base64!!"},
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_cursor_with_wrong_shape_returns_400(self, client, auth_headers):
        import base64, json

        bad_cursor = base64.urlsafe_b64encode(
            json.dumps({"foo": "bar"}).encode()
        ).decode()

        response = client.get(
            app.url_path_for(RouteName.INGREDIENT_LIST),
            params={"after": bad_cursor},
            headers=auth_headers,
        )
        assert response.status_code == 400
