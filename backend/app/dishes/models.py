from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.ingredients.models import Ingredient
import uuid
from sqlalchemy.dialects.postgresql import UUID
from app.core.mixins import PublicIdMixin, TimestampMixin, OwnedMixin, SoftDeleteMixin


class Dish(PublicIdMixin, TimestampMixin, OwnedMixin, SoftDeleteMixin, Base):
    __tablename__ = "dishes"

    id = Column(Integer, primary_key=True)
    public_id = Column(
        UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4, index=True
    )
    label = Column(String, nullable=True)
    comment = Column(String, nullable=True)
    main_ingredient_id = Column(Integer, ForeignKey("ingredients.id"), nullable=False)

    main_ingredient = relationship("Ingredient", foreign_keys=[main_ingredient_id])

    __table_args__ = (
        Index("ix_dishes_user_id_id", "user_id", "id"),
        Index("ix_dishes_main_ingredient_id", "main_ingredient_id"),
    )

    @property
    def display_label(self):
        if self.label:
            return self.label
        if self.main_ingredient:
            return self.main_ingredient.name
        return None
