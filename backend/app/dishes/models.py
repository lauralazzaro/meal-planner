from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.ingredients.models import Ingredient
import uuid
from sqlalchemy.dialects.postgresql import UUID


class Dish(Base):
    __tablename__ = "dishes"

    id = Column(Integer, primary_key=True, index=True)
    public_id = Column(
        UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4, index=True
    )
    label = Column(String, nullable=True)
    comment = Column(String, nullable=True)
    main_ingredient_id = Column(Integer, ForeignKey("ingredients.id"), nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    main_ingredient = relationship("Ingredient", foreign_keys=[main_ingredient_id])

    @property
    def display_label(self):
        if self.label:
            return self.label
        if self.main_ingredient:
            return self.main_ingredient.name
        return None
