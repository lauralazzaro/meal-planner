from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.ingredients import models, schemas
from app.core.crud_helpers import (
    get_owned_record,
    get_owned_paginated_records,
)


def get_ingredient(ingredient_public_id, user_id: int, db: Session):
    """Return a single non-deleted ingredient by public_id, owned by the given user."""
    return get_owned_record(
        models.Ingredient, ingredient_public_id, user_id, db, lookup_field="public_id"
    )


def get_paginated_ingredients(user_id, db, params):
    return get_owned_paginated_records(
        models.Ingredient, user_id, db, params, sort_field="name"
    )


def create_ingredient(ingredient: schemas.IngredientCreate, user_id: int, db: Session):
    """Add ingredients to pool
    First looks if it was already created and if is_deleted = True
    If true, set it back to false so it can be used again
    else simply add new ingredient to pool"""

    existing = (
        db.query(models.Ingredient)
        .filter(
            models.Ingredient.name == ingredient.name,
            models.Ingredient.user_id == user_id,
        )
        .first()
    )

    if existing and existing.is_deleted:
        existing.is_deleted = False
        existing.shopping_category = ingredient.shopping_category
        return existing

    new_ingredient = models.Ingredient(**ingredient.model_dump(), user_id=user_id)

    db.add(new_ingredient)
    db.flush()
    return new_ingredient


def update_ingredient(
    ingredient_public_id,
    user_id: int,
    ingredient_update: schemas.IngredientUpdate,
    db: Session,
):
    """Update one or more fields of an existing ingredient owned by the user."""
    ingredient = get_ingredient(ingredient_public_id, user_id, db)
    if not ingredient:
        return None
    for field, value in ingredient_update.model_dump(exclude_unset=True).items():
        setattr(ingredient, field, value)
    return ingredient


def delete_ingredient(ingredient_public_id, user_id: int, db: Session):
    """Soft delete an ingredient owned by the user."""
    ingredient = get_ingredient(ingredient_public_id, user_id, db)
    if not ingredient:
        return None

    ingredient.is_deleted = True
    return ingredient
