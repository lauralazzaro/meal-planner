import json
import os
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.ingredients.models import Ingredient
from app.dishes.models import Dish
from app.weekly_plans.models import WeeklyPlan, WeeklyPlanDish
from app.shopping_list.models import ShoppingList, ShoppingListItem
from app.auth.models import User
from app.core import security


def load_json(filename: str):
    """Load seed data from a JSON file."""
    filepath = os.path.join(os.path.dirname(__file__), filename)
    with open(filepath) as f:
        return json.load(f)


def seed_user(db: Session):
    """Create a default test user if it doesn't exist. Returns the user."""
    existing = db.query(User).filter(User.email == "test@test.com").first()
    if existing:
        return existing

    user = User(
        email="test@test.com",
        hashed_password=security.hash_password("password123"),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"Created test user: {user.email}")
    return user


def seed_ingredients(db: Session, user_id: int):
    """Insert ingredients if they don't already exist for this user."""
    data = load_json("ingredients.json")
    count = 0
    for item in data:
        exists = (
            db.query(Ingredient)
            .filter(Ingredient.name == item["name"], Ingredient.user_id == user_id)
            .first()
        )
        if not exists:
            db.add(Ingredient(**item, user_id=user_id))
            count += 1
    db.commit()
    print(f"Inserted {count} new ingredients.")


def seed_dishes(db: Session, user_id: int):
    """Insert dishes if they don't already exist for this user."""
    data = load_json("dishes.json")
    count = 0
    for item in data:
        exists = (
            db.query(Dish)
            .filter(Dish.label == item["label"], Dish.user_id == user_id)
            .first()
        )
        if not exists:
            ingredient = (
                db.query(Ingredient)
                .filter(
                    Ingredient.name == item["main_ingredient"],
                    Ingredient.user_id == user_id,
                )
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
                    user_id=user_id,
                )
            )
            count += 1
    db.commit()
    print(f"Inserted {count} new dishes.")


def seed_weekly_plans(db: Session, user_id: int):
    """Insert weekly plans if they don't already exist for this user."""
    data = load_json("weekly_plans.json")
    count = 0
    for plan_data in data:
        exists = (
            db.query(WeeklyPlan)
            .filter(WeeklyPlan.name == plan_data["name"], WeeklyPlan.user_id == user_id)
            .first()
        )
        if exists:
            continue

        plan = WeeklyPlan(
            name=plan_data["name"], is_default=plan_data["is_default"], user_id=user_id
        )
        db.add(plan)
        db.flush()

        for dish_data in plan_data["dishes"]:
            dish = (
                db.query(Dish)
                .filter(
                    Dish.label == dish_data["dish_label"],
                    Dish.user_id == user_id,
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


def seed_shopping_lists(db: Session, user_id: int):
    """Insert shopping lists with items if they don't already exist for this user."""
    data = load_json("shopping_lists.json")
    count = 0

    for list_data in data:
        exists = (
            db.query(ShoppingList)
            .filter(
                ShoppingList.name == list_data["name"], ShoppingList.user_id == user_id
            )
            .first()
        )
        if exists:
            continue

        shopping_list = ShoppingList(name=list_data["name"], user_id=user_id)
        db.add(shopping_list)
        db.flush()

        for item_data in list_data["items"]:
            if "ingredient_name" in item_data:
                ingredient = (
                    db.query(Ingredient)
                    .filter(
                        Ingredient.name == item_data["ingredient_name"],
                        Ingredient.user_id == user_id,
                    )
                    .first()
                )
                if not ingredient:
                    print(
                        f"Ingredient '{item_data['ingredient_name']}' not found, skipping item."
                    )
                    continue

                db.add(
                    ShoppingListItem(
                        shopping_list_id=shopping_list.id,
                        ingredient_id=ingredient.id,
                        name=ingredient.name,
                        shopping_category=ingredient.shopping_category,
                        quantity=item_data.get("quantity"),
                        unit=item_data.get("unit"),
                    )
                )
            else:
                db.add(
                    ShoppingListItem(
                        shopping_list_id=shopping_list.id,
                        name=item_data["name"],
                        shopping_category=item_data["shopping_category"],
                        quantity=item_data.get("quantity"),
                        unit=item_data.get("unit"),
                    )
                )

        count += 1

    db.commit()
    print(f"Inserted {count} new shopping lists.")


def run():
    db = SessionLocal()
    try:
        user = seed_user(db)
        seed_ingredients(db, user.id)
        seed_dishes(db, user.id)
        seed_weekly_plans(db, user.id)
        seed_shopping_lists(db, user.id)
    except Exception as e:
        print(f"Seed failed: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    run()
