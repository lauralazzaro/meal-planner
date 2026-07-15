from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, loaded from environment variables.

    This is the single source of truth for the API version prefix and any
    value derived from it (such as the OAuth2 token URL). Change API_V1_STR
    here and every consumer follows automatically.
    """

    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")

    PROJECT_NAME: str = "Meal Planner"
    API_V1_STR: str = "/api/v1"

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    DATABASE_URL: str

    @property
    def TOKEN_URL(self) -> str:
        """Relative path to the login endpoint, used by OAuth2PasswordBearer.

        Deliberately relative (no leading slash): FastAPI recommends this so the
        Swagger 'Authorize' button resolves the token URL correctly regardless
        of host, proxy, or root_path. Derived from API_V1_STR so it can never
        drift from the real route.
        """
        return f"{self.API_V1_STR.lstrip('/')}/auth/login"


settings = Settings()
