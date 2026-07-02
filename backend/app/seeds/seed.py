import json
import os
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.ingredients.models import Ingredient
from app.dishes.models import Dish
from app.weekly_plans.models import WeeklyPlan, WeeklyPlanDish


def load_json(filename: str):
    """Load seed data from a JSON file."""
    filepath = os.path.join(os.path.dirname(__file__), filename)
    with open(filepath) as f:
        return json.load(f)


def seed_ingredients(db: Session):
    """Insert ingredients if they don't already exist."""
    data = load_json("ingredients.json")
    print(f"Loaded {len(data)} items from JSON")
    count = 0
    for item in data:
        exists = db.query(Ingredient).filter(Ingredient.name == item["name"]).first()
        if not exists:
            db.add(Ingredient(**item))
            count += 1
    db.commit()
    print(f"Inserted {count} new ingredients.")


print(f"__name__ is: {__name__}")


def seed_dishes(db: Session):
    """Insert dishes if they don't already exist."""
    data = load_json("dishes.json")
    count = 0
    for item in data:
        exists = db.query(Dish).filter(Dish.label == item["label"]).first()
        if not exists:
            ingredient = (
                db.query(Ingredient)
                .filter(Ingredient.name == item["main_ingredient"])
                .first()
            )
            if not ingredient:
                print(
                    f"Ingredient '{item['main_ingredient']}' not found, skipping {item['label']}"
                )
                continue

            db.add(
                Dish(
                    label=item["label"],
                    main_ingredient_id=ingredient.id,
                )
            )
            count += 1

    db.commit()
    print(f"Inserted {count} new dishes.")


def seed_weekly_plans(db: Session):
    """Insert weekly plans if they don't already exist."""
    data = load_json("weekly_plans.json")
    count = 0

    for plan_data in data:
        exists = (
            db.query(WeeklyPlan).filter(WeeklyPlan.name == plan_data["name"]).first()
        )
        if exists:
            continue

        plan = WeeklyPlan(
            name=plan_data["name"],
            is_default=plan_data["is_default"],
        )
        db.add(plan)
        db.flush()

        for dish_data in plan_data["dishes"]:
            dish = (
                db.query(Dish)
                .filter(
                    Dish.label == dish_data["dish_label"],
                    Dish.is_deleted == False,
                )
                .first()
            )
            if not dish:
                print(f"Dish '{dish_data['dish_label']}' not found, skipping.")
                continue

            db.add(
                WeeklyPlanDish(
                    weekly_plan_id=plan.id,
                    day_of_week=dish_data["day_of_week"],
                    meal_type=dish_data["meal_type"],
                    dish_id=dish.id,
                )
            )

        count += 1

    db.commit()
    print(f"Inserted {count} new weekly plans.")


def run():
    db = SessionLocal()
    try:
        seed_ingredients(db)
        seed_dishes(db)
        seed_weekly_plans(db)
    except Exception as e:
        print(f"Seed failed: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    run()
