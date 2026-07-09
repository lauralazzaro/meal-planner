from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.ingredients import crud, schemas
from app.auth.security import get_current_user
from app.auth.models import User

router = APIRouter(prefix="/ingredients", tags=["ingredients"])


@router.get("/", response_model=list[schemas.IngredientOut])
def read_all_ingredients(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Return all ingredients owned by the current user."""
    return crud.get_all_ingredients(current_user.id, db)


@router.get("/{ingredient_id}", response_model=schemas.IngredientOut)
def read_ingredient(
    ingredient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return a single ingredient by id, owned by the current user."""
    ingredient = crud.get_ingredient(ingredient_id, current_user.id, db)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient


@router.post("/", response_model=schemas.IngredientOut)
def create_ingredient(
    ingredient: schemas.IngredientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a new ingredient to the pool."""
    try:
        return crud.create_ingredient(ingredient, current_user.id, db)
    except IntegrityError:
        raise HTTPException(
            status_code=409, detail="An ingredient with this name already exists"
        )


@router.patch("/{ingredient_id}", response_model=schemas.IngredientOut)
def update_ingredient(
    ingredient_id: int,
    ingredient_update: schemas.IngredientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update one or more fields of an existing ingredient."""
    ingredient = crud.update_ingredient(
        ingredient_id, current_user.id, ingredient_update, db
    )
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient


@router.delete("/{ingredient_id}")
def delete_ingredient(
    ingredient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark an ingredient as deleted."""
    ingredient = crud.delete_ingredient(ingredient_id, current_user.id, db)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return {"status": "Ingredient marked as deleted"}
