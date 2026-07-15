"""Contract tests for the API routing layer.

These guard the reverse-routing invariants so that a mistake in a path, a
missing route name, or a drift between the OAuth2 token URL and the real login
route fails at build time (a red test) instead of silently at runtime (a 404
on the Swagger 'Authorize' button, or a broken client).
"""

from app.main import app
from app.core.config import settings
from app.core.route_names import RouteName


def _named_api_routes():
    """Yield the app routes that carry an explicit endpoint name."""
    for route in app.routes:
        name = getattr(route, "name", None)
        path = getattr(route, "path", "")
        # skip FastAPI's own utility routes (docs, openapi, redoc, root)
        if name and path.startswith(settings.API_V1_STR):
            yield route


class TestRouteNames:
    def test_every_api_route_uses_a_known_name(self):
        """Each mounted API route must declare a name from the RouteName enum.

        Without this, url_path_for() would raise at runtime the first time a
        test or redirect referenced the route.
        """
        valid = set(RouteName)
        for route in _named_api_routes():
            assert route.name in valid, (
                f"Route {route.path!r} has name {route.name!r}, "
                f"which is not declared in RouteName"
            )

    def test_auth_routes_are_reachable_by_name(self):
        """The auth route names must resolve to the expected paths."""
        assert (
            app.url_path_for(RouteName.AUTH_LOGIN)
            == f"{settings.API_V1_STR}/auth/login"
        )
        assert (
            app.url_path_for(RouteName.AUTH_REGISTER)
            == f"{settings.API_V1_STR}/auth/register"
        )


class TestTokenUrlConsistency:
    def test_token_url_matches_the_real_login_route(self):
        """The OAuth2 tokenUrl in the OpenAPI schema must point at the login
        route that actually exists -- this is the exact drift that broke the
        Swagger 'Authorize' lock.
        """
        schema = app.openapi()
        flows = schema["components"]["securitySchemes"]["OAuth2PasswordBearer"]["flows"]
        token_url = flows["password"]["tokenUrl"]

        login_path = app.url_path_for(RouteName.AUTH_LOGIN)
        # tokenUrl is relative (no leading slash); normalise before comparing
        assert login_path.endswith(
            token_url
        ), f"tokenUrl {token_url!r} does not match login route {login_path!r}"
