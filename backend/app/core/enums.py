from enum import Enum
from sqlalchemy import CheckConstraint


class DayOfWeek(str, Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"


class MealType(str, Enum):
    BREAKFAST = "BREAKFAST"
    LUNCH = "LUNCH"
    DINNER = "DINNER"


class ShoppingCategory(str, Enum):
    VEGETABLES = "VEGETABLES"
    FRUIT = "FRUIT"
    MEAT_AND_FISH = "MEAT_AND_FISH"
    PASTA_AND_GRAINS = "PASTA_AND_GRAINS"
    DAIRY = "DAIRY"
    PANTRY = "PANTRY"
    BEVERAGES = "BEVERAGES"
    HOUSEHOLD = "HOUSEHOLD"
    OTHER = "OTHER"


def enum_check(column: str, enum_cls, name: str) -> CheckConstraint:
    """Build a CHECK constraint whose allowed values come from the enum,
    so the two can never drift apart."""
    values = ", ".join(f"'{member.value}'" for member in enum_cls)
    return CheckConstraint(f"{column} IN ({values})", name=name)
