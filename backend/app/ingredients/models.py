from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from app.database import Base


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    shopping_category = Column(String, nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("name", "user_id", name="uq_ingredient_name_per_user"),
    )
