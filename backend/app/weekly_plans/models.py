from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
from app.database import Base
from app.dishes.models import Dish
from app.core.mixins import PublicIdMixin, TimestampMixin, OwnedMixin
from app.core.enums import DayOfWeek, MealType, enum_check


class WeeklyPlan(PublicIdMixin, TimestampMixin, OwnedMixin, Base):
    __tablename__ = "weekly_plans"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=True)
    is_default = Column(Boolean, nullable=False, default=False)

    dishes = relationship(
        "WeeklyPlanDish",
        back_populates="weekly_plan",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        Index(
            "uq_one_default_weekly_plan_per_user",
            "is_default",
            "user_id",
            unique=True,
            postgresql_where=(is_default == True),
        ),
        Index("ix_weekly_plans_user_id_id", "user_id", "id"),
    )


class WeeklyPlanDish(Base):
    """Represents a dish associated to a weekly meal plan"""

    __tablename__ = "weekly_plan_dishes"

    id = Column(Integer, primary_key=True)
    day_of_week = Column(String, nullable=False)
    meal_type = Column(String, nullable=False)
    weekly_plan_id = Column(
        Integer, ForeignKey("weekly_plans.id", ondelete="CASCADE"), nullable=False
    )
    dish_id = Column(
        Integer, ForeignKey("dishes.id", ondelete="CASCADE"), nullable=False
    )

    weekly_plan = relationship("WeeklyPlan", back_populates="dishes")
    dish = relationship("Dish")

    __table_args__ = (
        enum_check("day_of_week", DayOfWeek, "ck_weekly_plan_dishes_day_of_week"),
        enum_check("meal_type", MealType, "ck_weekly_plan_dishes_meal_type"),
        Index("ix_weekly_plan_dishes_weekly_plan_id", "weekly_plan_id"),
        Index("ix_weekly_plan_dishes_dish_id", "dish_id"),
    )
