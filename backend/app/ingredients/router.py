from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db
from sqlalchemy.orm import Session
from app.ingredients import crud, schemas

router = APIRouter(prefix="/ingredients", tags=["ingredients"])


@router.get("/{ingredient_id}", response_model=schemas.IngredientOut)
def read_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    ingredient = crud.get_ingredient(ingredient_id, db)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient


@router.get("/", response_model=list[schemas.IngredientOut])
def read_all_ingredients(db: Session = Depends(get_db)):
    return crud.get_all_ingredients(db)


@router.post("/", response_model=schemas.IngredientOut)
def create_ingredient(
    ingredient: schemas.IngredientCreate, db: Session = Depends(get_db)
):
    return crud.create_ingredient(ingredient, db)


@router.patch("/{ingredient_id}", response_model=schemas.IngredientOut)
def update_ingredient(
    ingredient_id: int,
    ingredient_update: schemas.IngredientUpdate,
    db: Session = Depends(get_db),
):
    ingredient = crud.update_ingredient(ingredient_id, ingredient_update, db)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient


@router.delete("/{ingredient_id}")
def delete_ingredient(ingredient_id, db: Session = Depends(get_db)):
    ingredient = crud.delete_ingredient(ingredient_id, db)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return {"status": "Ingredient marked as deleted"}
