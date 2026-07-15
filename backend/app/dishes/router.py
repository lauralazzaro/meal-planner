from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dishes import crud, schemas
from app.auth.models import User
from app.core.dependencies import get_current_user
from app.core.route_names import RouteName

router = APIRouter(prefix="/dishes", tags=["dishes"])


@router.get("/", response_model=list[schemas.DishOut], name=RouteName.DISH_LIST)
def read_all_dishes(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Return all non-deleted dishes."""

    return crud.get_all_dishes(current_user.id, db)


@router.get("/{dish_id}", response_model=schemas.DishOut, name=RouteName.DISH_DETAIL)
def read_one_dish(
    dish_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return a single dish by id. Raises 404 if not found or deleted."""

    dish = crud.get_one_dish(dish_id, current_user.id, db)
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    return dish


@router.post("/", response_model=schemas.DishOut, name=RouteName.DISH_CREATE)
def create_dish(
    dish: schemas.DishCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new dish linked to an existing ingredient. Raises 404 if ingredient not found."""

    new_dish = crud.create_dish(dish, current_user.id, db)
    if not new_dish:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return new_dish


@router.patch("/{dish_id}", response_model=schemas.DishOut, name=RouteName.DISH_UPDATE)
def update_dish(
    dish_id: int,
    dish_update: schemas.DishUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update one or more fields of an existing dish. Raises 404 if not found."""

    dish = crud.update_dish(dish_id, current_user.id, dish_update, db)
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")

    return dish


@router.delete("/{dish_id}", name=RouteName.DISH_DELETE)
def delete_dish(
    dish_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a dish as deleted. Raises 404 if not found."""

    dish = crud.delete_dish(dish_id, current_user.id, db)
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    return {"status": "Dish marked as deleted"}
