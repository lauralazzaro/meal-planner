import uuid
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Index, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.dishes.models import Dish


class WeeklyPlan(Base):
    __tablename__ = "weekly_plan"

    id = Column(Integer, primary_key=True)
    public_id = Column(
        UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4, index=True
    )
    name = Column(String, nullable=True)
    is_default = Column(Boolean, nullable=False, default=False)
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
        Index("ix_weekly_plan_user_id_id", "user_id", "id"),
    )


class WeeklyPlanDish(Base):
    """Represents a dish associated to a weekly meal plan"""

    __tablename__ = "weekly_plan_dish"

    id = Column(Integer, primary_key=True)
    day_of_week = Column(String, nullable=False)
    meal_type = Column(String, nullable=False)
    weekly_plan_id = Column(Integer, ForeignKey("weekly_plan.id"), nullable=False)
    dish_id = Column(Integer, ForeignKey("dishes.id"), nullable=False)

    weekly_plan = relationship("WeeklyPlan", back_populates="dishes")
    dish = relationship("Dish")

    __table_args__ = (
        Index("ix_weekly_plan_dish_weekly_plan_id", "weekly_plan_id"),
        Index("ix_weekly_plan_dish_dish_id", "dish_id"),
    )
