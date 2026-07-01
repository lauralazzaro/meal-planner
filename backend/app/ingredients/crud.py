from sqlalchemy.orm import Session
from app.ingredients import models, schemas


def get_ingredient(ingredient_id: int, db: Session):
    return (
        db.query(models.Ingredient)
        .filter(models.Ingredient.id == ingredient_id, models.Ingredient.is_deleted == False)
        .first()
    )

def get_all_ingredients(db: Session):
    return (
        db.query(models.Ingredient)
        .filter(models.Ingredient.is_deleted == False)
        .order_by(models.Ingredient.shopping_category)
        .all()
    )


def create_ingredient(ingredient: schemas.IngredientCreate, db: Session):
    new_ingredient = models.Ingredient(**ingredient.model_dump())
    db.add(new_ingredient)
    db.commit()
    db.refresh(new_ingredient)
    return new_ingredient

def update_ingredient(ingredient_id: int, ingredient_update: schemas.IngredientUpdate, db: Session):
    ingredient = (
        db.query(models.Ingredient)
        .filter(models.Ingredient.id == ingredient_id, models.Ingredient.is_deleted == False)
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
    ingredient = (
        db.query(models.Ingredient)
        .filter(models.Ingredient.id == ingredient_id, models.Ingredient.is_deleted == False)
        .first()
    )

    if not ingredient:
        return None
    
    ingredient.is_deleted = True
    db.commit()
    db.refresh(ingredient)

    return ingredient