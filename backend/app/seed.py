from app.database import SessionLocal
from app import models


def seed():
    db = SessionLocal()

    tomato = models.Ingredient(name="Pomodoro", shopping_category="vegetables")
    pasta = models.Ingredient(name="Pasta", shopping_category="pantry")
    db.add_all([tomato, pasta])
    db.flush()

    dish = models.Dish(
        name="Pasta al pomodoro",
        meal_type="both",
        nutritional_tags=["carbs", "vegetables"],
    )
    db.add(dish)
    db.flush()

    db.add(models.DishIngredient(dish_id=dish.id, ingredient_id=tomato.id, quantity=200, unit="g"))
    db.add(models.DishIngredient(dish_id=dish.id, ingredient_id=pasta.id))

    db.commit()
    db.close()
    print("Seed completed.")


if __name__ == "__main__":
    seed()