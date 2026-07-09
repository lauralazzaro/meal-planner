from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.ingredients import crud, schemas
from app.auth.security import get_current_user

router = APIRouter(
    prefix="/ingredients",
    tags=["ingredients"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/{ingredient_id}", response_model=schemas.IngredientOut)
def read_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    """Return a single ingredient by id. Raises 404 if not found or deleted."""

    ingredient = crud.get_ingredient(ingredient_id, db)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient


@router.get("/", response_model=list[schemas.IngredientOut])
def read_all_ingredients(db: Session = Depends(get_db)):
    """Return all ingredients ordered by shopping category."""

    return crud.get_all_ingredients(db)


@router.post("/", response_model=schemas.IngredientOut)
def create_ingredient(
    ingredient: schemas.IngredientCreate, db: Session = Depends(get_db)
):
    """Add a new ingredient to the pool."""

    try:
        return crud.create_ingredient(ingredient, db)
    except IntegrityError:
        raise HTTPException(
            status_code=409, detail="An ingredient with this name already exists"
        )


@router.patch("/{ingredient_id}", response_model=schemas.IngredientOut)
def update_ingredient(
    ingredient_id: int,
    ingredient_update: schemas.IngredientUpdate,
    db: Session = Depends(get_db),
):
    """Update one or more fields of an existing ingredient. Raises 404 if not found."""

    ingredient = crud.update_ingredient(ingredient_id, ingredient_update, db)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient


@router.delete("/{ingredient_id}")
def delete_ingredient(ingredient_id, db: Session = Depends(get_db)):
    """Mark an ingredient as deleted. Raises 404 if not found."""

    ingredient = crud.delete_ingredient(ingredient_id, db)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return {"status": "Ingredient marked as deleted"}
