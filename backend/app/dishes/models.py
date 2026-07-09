from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from app.ingredients.models import Ingredient


class Dish(Base):
    __tablename__ = "dishes"

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String, nullable=True)
    comment = Column(String, nullable=True)
    main_ingredient_id = Column(Integer, ForeignKey("ingredients.id"), nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    main_ingredient = relationship("Ingredient", foreign_keys=[main_ingredient_id])

    @property
    def display_label(self):
        if self.label:
            return self.label
        if self.main_ingredient:
            return self.main_ingredient.name
        return None
