from sqlalchemy.orm import Session
from app.dishes import models, schemas
from app.ingredients.models import Ingredient
from app.core.crud_helpers import (
    get_owned_record,
    get_all_owned_records,
    get_owned_paginated_records,
)


def get_one_dish(dish_id, user_id: int, db: Session):
    """Return a single non-deleted dish by public_id, owned by the given user."""
    return get_owned_record(models.Dish, dish_id, user_id, db, lookup_field="public_id")


def get_all_dishes(user_id: int, db: Session):
    """Return all non-deleted dishes owned by the given user."""
    return get_all_owned_records(models.Dish, user_id, db)


def get_paginated_dishes(user_id, db, params):
    return get_owned_paginated_records(
        models.Dish, user_id, db, params, sort_field="id"
    )


def create_dish(dish: schemas.DishCreate, user_id: int, db: Session):
    """Create a new dish linked to an existing ingredient owned by the same user."""
    ingredient = (
        db.query(Ingredient)
        .filter(
            Ingredient.public_id == dish.main_ingredient_public_id,
            Ingredient.user_id == user_id,
            Ingredient.is_deleted == False,
        )
        .first()
    )
    if not ingredient:
        return None

    new_dish = models.Dish(
        label=dish.label,
        comment=dish.comment,
        main_ingredient_id=ingredient.id,
        user_id=user_id,
    )

    db.add(new_dish)
    db.commit()
    db.refresh(new_dish)
    return new_dish


def update_dish(
    dish_public_id, user_id: int, dish_update: schemas.DishUpdate, db: Session
):
    """Update one or more fields of an existing dish owned by the user."""
    dish = get_one_dish(dish_public_id, user_id, db)
    if not dish:
        return None

    update_data = dish_update.model_dump(exclude_unset=True)

    # main_ingredient_public_id needs resolving to the internal id before
    # it can be assigned to the model's main_ingredient_id column.
    if "main_ingredient_public_id" in update_data:
        new_public_id = update_data.pop("main_ingredient_public_id")
        ingredient = (
            db.query(Ingredient)
            .filter(
                Ingredient.public_id == new_public_id,
                Ingredient.user_id == user_id,
                Ingredient.is_deleted == False,
            )
            .first()
        )
        if not ingredient:
            return None
        dish.main_ingredient_id = ingredient.id

    for field, value in update_data.items():
        setattr(dish, field, value)

    db.commit()
    db.refresh(dish)
    return dish


def delete_dish(dish_public_id, user_id: int, db: Session):
    """Soft delete a dish owned by the user."""
    dish = get_one_dish(dish_public_id, user_id, db)
    if not dish:
        return None

    dish.is_deleted = True
    db.commit()
    db.refresh(dish)
    return dish
