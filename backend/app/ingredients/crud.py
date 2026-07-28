from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.ingredients import models, schemas
from app.core.crud_helpers import (
    get_owned_record,
    get_all_owned_records,
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
    """Add a new ingredient to the pool for the given user."""
    new_ingredient = models.Ingredient(**ingredient.model_dump(), user_id=user_id)
    db.add(new_ingredient)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(new_ingredient)
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

    update_data = ingredient_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ingredient, field, value)

    db.commit()
    db.refresh(ingredient)
    return ingredient


def delete_ingredient(ingredient_public_id, user_id: int, db: Session):
    """Soft delete an ingredient owned by the user."""
    ingredient = get_ingredient(ingredient_public_id, user_id, db)
    if not ingredient:
        return None

    ingredient.is_deleted = True
    db.commit()
    db.refresh(ingredient)
    return ingredient
