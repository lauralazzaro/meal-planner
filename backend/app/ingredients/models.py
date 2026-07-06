from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.dialects.postgresql import ARRAY
from app.database import Base


class Ingredient(Base):
    """Represents an ingredient in the shared pool.
    Used as a reference for dishes and shopping lists."""

    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    shopping_category = Column(String, nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
