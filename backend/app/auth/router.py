from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.database import get_db
from app.auth import crud, schemas
from app.core import security
from app.core.route_names import RouteName

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserOut, name=RouteName.AUTH_REGISTER)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    new_user = crud.create_user(user, db)
    if not new_user:
        raise HTTPException(status_code=409, detail="Email already registered")
    return new_user


@router.post("/login", response_model=schemas.Token, name=RouteName.AUTH_LOGIN)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """Authenticate a user and return a JWT access token."""
    user = crud.authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    access_token = security.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
