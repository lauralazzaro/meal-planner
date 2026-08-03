import json
from pathlib import Path
from app.core.enums import ShoppingCategory, DayOfWeek, MealType

SEEDS = Path(__file__).parents[2] / "app" / "seeds"


def test_seed_categories_are_valid():
    valid = {c.value for c in ShoppingCategory}
    for item in json.loads((SEEDS / "ingredients.json").read_text()):
        assert item["shopping_category"] in valid


def test_seed_days_and_meals_are_valid():
    days = {d.value for d in DayOfWeek}
    meals = {m.value for m in MealType}
    for plan in json.loads((SEEDS / "weekly_plans.json").read_text()):
        for dish in plan["dishes"]:
            assert dish["day_of_week"] in days
            assert dish["meal_type"] in meals
