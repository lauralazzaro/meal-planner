from app.main import app
from app.core.route_names import RouteName


class TestAuth:
    def test_password_over_72_bytes_returns_422(self, client):
        response = client.post(
            app.url_path_for(RouteName.AUTH_REGISTER),
            json={"email": "a@test.com", "password": "à" * 40},  # 80 byte, 40 caratteri
        )
        assert response.status_code == 422
