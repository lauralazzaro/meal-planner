from sqlalchemy.orm import Session
from app.dishes import models, schemas
from app.ingredients.models import Ingredient


def get_all_dishes(db: Session):
    """Return all non-deleted dishes"""
    return db.query(models.Dish).filter(models.Dish.is_deleted == False).all()


def get_one_dish(dish_id: int, db: Session):
    """Return one dish by id. Raise 404 if not found or deleted"""
    dish = (
        db.query(models.Dish)
        .filter(models.Dish.id == dish_id, models.Dish.is_deleted == False)
        .first()
    )

    if not dish:
        return None

    return dish


def create_dish(dish: schemas.DishCreate, db: Session):
    """Create a dish using an ingredient in the system."""
    ingredient = (
        db.query(Ingredient)
        .filter(
            Ingredient.id == dish.main_ingredient_id, Ingredient.is_deleted == False
        )
        .first()
    )
    if not ingredient:
        return None

    new_dish = models.Dish(**dish.model_dump())
    db.add(new_dish)
    db.commit()
    db.refresh(new_dish)
    return new_dish


def update_dish(dish_id: int, dish_update: schemas.DishUpdate, db: Session):
    """Update a dish in the system"""
    dish = (
        db.query(models.Dish)
        .filter(models.Dish.id == dish_id, models.Dish.is_deleted == False)
        .first()
    )

    if not dish:
        return None

    ingredient = (
        db.query(Ingredient)
        .filter(
            Ingredient.id == dish.main_ingredient_id, Ingredient.is_deleted == False
        )
        .first()
    )
    if not ingredient:
        return None

    update_data = dish_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(dish, field, value)

    db.commit()
    db.refresh(dish)

    return dish


def delete_dish(dish_id: int, db: Session):
    """Mark a dish as deleted"""
    dish = (
        db.query(models.Dish)
        .filter(models.Dish.id == dish_id, models.Dish.is_deleted == False)
        .first()
    )

    if not dish:
        return None

    dish.is_deleted = True
    db.commit()
    db.refresh(dish)

    return dish
