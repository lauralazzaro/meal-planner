from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.ingredients.models import Ingredient  # noqa: F401
import uuid
from sqlalchemy.dialects.postgresql import UUID
from app.core.mixins import PublicIdMixin, TimestampMixin, OwnedMixin


class ShoppingList(PublicIdMixin, TimestampMixin, OwnedMixin, Base):
    __tablename__ = "shopping_lists"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=True)

    items = relationship(
        "ShoppingListItem",
        back_populates="shopping_list",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (Index("ix_shopping_lists_user_id_id", "user_id", "id"),)


class ShoppingListItem(Base):
    """A single item in a shopping list. Can be linked to an existing
    Ingredient from the pool, or be a free-text entry."""

    __tablename__ = "shopping_list_items"

    id = Column(Integer, primary_key=True)
    shopping_list_id = Column(
        Integer, ForeignKey("shopping_lists.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String, nullable=False)
    shopping_category = Column(String, nullable=False)
    quantity = Column(Integer, nullable=True)
    unit = Column(String, nullable=True)
    is_checked = Column(Boolean, nullable=False, default=False)
    ingredient_id = Column(
        Integer, ForeignKey("ingredients.id", ondelete="SET NULL"), nullable=True
    )

    shopping_list = relationship("ShoppingList", back_populates="items")
    ingredient = relationship("Ingredient")

    __table_args__ = (
        Index("ix_shopping_list_items_shopping_list_id", "shopping_list_id"),
        Index("ix_shopping_list_items_ingredient_id", "ingredient_id"),
    )

    @property
    def ingredient_public_id(self):
        """Expose the linked ingredient's public_id, if any, for API responses."""
        return self.ingredient.public_id if self.ingredient else None
