import uuid
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.core.schemas import PublicIdSchema


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt(cls, v: str) -> str:
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password too long (max 72 bytes)")
        return v


class UserOut(PublicIdSchema):
    email: EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
