from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import crud
from app.core.security import decode_access_token, oauth2_scheme
from app.database import get_db

# FastAPI dependencies that need feature modules live here, separate from the
# pure infrastructure in security.py. This is the layer allowed to depend on
# app.auth.crud without creating an import cycle.


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """Extract and validate the current user from the JWT token.

    Raises 401 if the token is invalid, expired, or the user doesn't exist.
    """
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    email = payload.get("sub")
    user = crud.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    return user
