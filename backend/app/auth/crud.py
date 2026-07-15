from sqlalchemy.orm import Session
from app.auth import models, schemas
from app.core import security


def get_user_by_email(email: str, db: Session):
    """Return a user by email, or None if not found."""
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(user: schemas.UserCreate, db: Session):
    """Create a new user with a hashed password.
    Returns None if the email is already registered."""
    existing = get_user_by_email(user.email, db)
    if existing:
        return None

    new_user = models.User(
        email=user.email,
        hashed_password=security.hash_password(user.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def authenticate_user(email: str, password: str, db: Session):
    """Verify credentials. Returns the user if valid, None otherwise."""
    user = get_user_by_email(email, db)
    if not user:
        return None
    if not security.verify_password(password, user.hashed_password):
        return None
    return user
