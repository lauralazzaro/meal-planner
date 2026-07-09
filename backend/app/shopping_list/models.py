from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.ingredients.models import Ingredient  # noqa: F401


class ShoppingList(Base):
    """A shopping list, containing multiple items."""

    __tablename__ = "shopping_lists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    items = relationship(
        "ShoppingListItem", back_populates="shopping_list", cascade="all, delete-orphan"
    )


class ShoppingListItem(Base):
    """A single item in a shopping list. Can be linked to an existing
    Ingredient from the pool, or be a free-text entry."""

    __tablename__ = "shopping_list_items"

    id = Column(Integer, primary_key=True, index=True)
    shopping_list_id = Column(Integer, ForeignKey("shopping_lists.id"), nullable=False)
    name = Column(String, nullable=False)
    shopping_category = Column(String, nullable=False)
    quantity = Column(Integer, nullable=True)
    unit = Column(String, nullable=True)
    is_checked = Column(Boolean, nullable=False, default=False)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), nullable=True)

    shopping_list = relationship("ShoppingList", back_populates="items")
