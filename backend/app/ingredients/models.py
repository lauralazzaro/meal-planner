from sqlalchemy import Column, Integer, String
from app.database import Base
from sqlalchemy import UniqueConstraint, Index
from app.core.mixins import PublicIdMixin, TimestampMixin, OwnedMixin, SoftDeleteMixin
from app.core.enums import ShoppingCategory, enum_check


class Ingredient(PublicIdMixin, TimestampMixin, OwnedMixin, SoftDeleteMixin, Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    shopping_category = Column(String, nullable=False)

    __table_args__ = (
        enum_check(
            "shopping_category", ShoppingCategory, "ck_ingredients_shopping_category"
        ),
        UniqueConstraint("name", "user_id", name="uq_ingredient_name_per_user"),
        Index("ix_ingredients_user_id_name", "user_id", "name"),
    )
