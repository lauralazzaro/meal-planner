from app.core.route_names import RouteName
from app.core.pagination import DEFAULT_LIMIT, MAX_LIMIT, encode_cursor
from app.main import app
from tests.conftest import create_test_ingredient
import base64, json, uuid


class TestPagination:
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

    def test_limit_at_max_is_accepted(self, client, auth_headers):
        """MAX_LIMIT itself is a valid value, not an off-by-one 422."""
        response = client.get(
            app.url_path_for(RouteName.INGREDIENT_LIST),
            params={"limit": MAX_LIMIT},
            headers=auth_headers,
        )
        assert response.status_code == 200

    def test_malformed_cursor_returns_400(self, client, auth_headers):
        response = client.get(
            app.url_path_for(RouteName.INGREDIENT_LIST),
            params={"after": "not-valid-base64!!"},
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_cursor_with_wrong_shape_returns_400(self, client, auth_headers):

        bad_cursor = base64.urlsafe_b64encode(
            json.dumps({"foo": "bar"}).encode()
        ).decode()

        response = client.get(
            app.url_path_for(RouteName.INGREDIENT_LIST),
            params={"after": bad_cursor},
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_default_limit_is_applied_when_not_specified(self, client, auth_headers):
        for i in range(DEFAULT_LIMIT + 1):
            create_test_ingredient(client, auth_headers, name=f"Ingrediente {i}")

        response = client.get(
            app.url_path_for(RouteName.INGREDIENT_LIST),
            headers=auth_headers,
        )

        data = response.json()
        assert len(data["items"]) == DEFAULT_LIMIT
        assert data["has_next"] is True

    def test_cursor_past_last_item_returns_empty_page(self, client, auth_headers):
        """A well-formed cursor that sorts after every row must not error --
        it should behave like 'there is nothing more to page through'."""
        create_test_ingredient(client, auth_headers, name="Aglio")
        create_test_ingredient(client, auth_headers, name="Basilico")

        cursor = encode_cursor("zzzzzzzz", str(uuid.uuid4()))

        response = client.get(
            app.url_path_for(RouteName.INGREDIENT_LIST),
            params={"after": cursor},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["has_next"] is False
        assert data["next_cursor"] is None

    def test_cursor_does_not_leak_internal_ids(self, client, auth_headers):
        for i in range(3):
            create_test_ingredient(client, auth_headers, name=f"Ingrediente {i}")

        response = client.get(
            app.url_path_for(RouteName.INGREDIENT_LIST),
            params={"limit": 2},
            headers=auth_headers,
        )
        payload = json.loads(base64.urlsafe_b64decode(response.json()["next_cursor"]))

        assert not isinstance(payload["t"], int)
        uuid.UUID(payload["t"])
