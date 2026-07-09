from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import crud, schemas, security

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    new_user = crud.create_user(user, db)
    if not new_user:
        raise HTTPException(status_code=409, detail="Email already registered")
    return new_user


@router.post("/login", response_model=schemas.Token)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """Authenticate a user and return a JWT access token."""
    user = crud.authenticate_user(credentials.email, credentials.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = security.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
