from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dishes import crud, schemas
from app.auth.security import get_current_user
from app.auth.models import User

router = APIRouter(prefix="/dishes", tags=["dishes"])


@router.get("/", response_model=list[schemas.DishOut])
def read_all_dishes(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Return all non-deleted dishes."""

    return crud.get_all_dishes(db)


@router.get("/{dish_id}", response_model=schemas.DishOut)
def read_one_dish(dish_id: int, db: Session = Depends(get_db)):
    """Return a single dish by id. Raises 404 if not found or deleted."""

    dish = crud.get_one_dish(dish_id, db)
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    return dish


@router.post("/", response_model=schemas.DishOut)
def create_dish(dish: schemas.DishCreate, db: Session = Depends(get_db)):
    """Create a new dish linked to an existing ingredient. Raises 404 if ingredient not found."""

    new_dish = crud.create_dish(dish, db)
    if not new_dish:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return new_dish


@router.patch("/{dish_id}", response_model=schemas.DishOut)
def update_dish(
    dish_id: int, dish_update: schemas.DishUpdate, db: Session = Depends(get_db)
):
    """Update one or more fields of an existing dish. Raises 404 if not found."""

    dish = crud.update_dish(dish_id, dish_update, db)
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")

    return dish


@router.delete("/{dish_id}")
def delete_dish(dish_id: int, db: Session = Depends(get_db)):
    """Mark a dish as deleted. Raises 404 if not found."""

    dish = crud.delete_dish(dish_id, db)
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    return {"status": "Dish marked as deleted"}
