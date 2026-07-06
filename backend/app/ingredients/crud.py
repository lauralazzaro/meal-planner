from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.ingredients import models, schemas


def get_ingredient(ingredient_id: int, db: Session):
    """Return a single non-deleted ingredient by id."""

    return (
        db.query(models.Ingredient)
        .filter(
            models.Ingredient.id == ingredient_id, models.Ingredient.is_deleted == False
        )
        .first()
    )


def get_all_ingredients(db: Session):
    """Return all non-deleted ingredients ordered by category."""

    return (
        db.query(models.Ingredient)
        .filter(models.Ingredient.is_deleted == False)
        .order_by(models.Ingredient.shopping_category)
        .all()
    )


def create_ingredient(ingredient: schemas.IngredientCreate, db: Session):
    """
    Add a new ingredient to the pool.
    Raises IntegrityError if name already exists.
    """

    new_ingredient = models.Ingredient(**ingredient.model_dump())
    db.add(new_ingredient)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(new_ingredient)
    return new_ingredient


def update_ingredient(
    ingredient_id: int, ingredient_update: schemas.IngredientUpdate, db: Session
):
    """Update one or more fields of an existing ingredient."""

    ingredient = (
        db.query(models.Ingredient)
        .filter(
            models.Ingredient.id == ingredient_id, models.Ingredient.is_deleted == False
        )
        .first()
    )

    if not ingredient:
        return None

    update_data = ingredient_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ingredient, field, value)

    db.commit()
    db.refresh(ingredient)

    return ingredient


def delete_ingredient(ingredient_id: int, db: Session):
    """Soft delete an ingredient by setting is_deleted to True."""

    ingredient = (
        db.query(models.Ingredient)
        .filter(
            models.Ingredient.id == ingredient_id, models.Ingredient.is_deleted == False
        )
        .first()
    )

    if not ingredient:
        return None

    ingredient.is_deleted = True
    db.commit()
    db.refresh(ingredient)

    return ingredient
