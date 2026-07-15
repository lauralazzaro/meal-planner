from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi.security import OAuth2PasswordBearer
from jose import jwt

from app.core.config import settings

# Pure security infrastructure: no dependency on any feature module.
# The get_current_user dependency lives in app/core/dependencies.py instead,
# because it needs app.auth.crud -- keeping it out of here avoids a circular
# import (crud -> security -> crud).

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.TOKEN_URL)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(data: dict) -> str:
    """Create a signed JWT containing the given data, with an expiration."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """Decode and verify a JWT. Returns the payload, or None if invalid/expired."""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except jwt.JWTError:
        return None
