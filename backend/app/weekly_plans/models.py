from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Boolean,
    Index,
)
from sqlalchemy.orm import relationship
from app.database import Base
from app.dishes.models import Dish


class WeeklyPlan(Base):
    __tablename__ = "weekly_plan"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    is_default = Column(Boolean, nullable=False, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    dishes = relationship(
        "WeeklyPlanDish", back_populates="weekly_plan", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index(
            "uq_one_default_weekly_plan_per_user",
            "is_default",
            "user_id",
            unique=True,
            postgresql_where=(is_default == True),
        ),
    )


class WeeklyPlanDish(Base):
    """Represents a dish associated to a weekly meal plan"""

    __tablename__ = "weekly_plan_dish"

    id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(String, nullable=False)
    meal_type = Column(String, nullable=False)
    weekly_plan_id = Column(Integer, ForeignKey("weekly_plan.id"), nullable=False)
    dish_id = Column(Integer, ForeignKey("dishes.id"), nullable=False)

    weekly_plan = relationship("WeeklyPlan", back_populates="dishes")
    dish = relationship("Dish")
