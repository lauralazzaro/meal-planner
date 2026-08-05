from fastapi import APIRouter, HTTPException
from app.dishes import crud, schemas
from app.core.dependencies import DbSession, CurrentUser
from app.core.route_names import RouteName
from app.core.pagination import PaginationQuery, Page
import uuid

router = APIRouter(prefix="/dishes", tags=["dishes"])


@router.get(
    "/",
    response_model=Page[schemas.DishOut],
    name=RouteName.DISH_LIST,
    response_model_by_alias=False,
)
def read_all_dishes(db: DbSession, current_user: CurrentUser, params: PaginationQuery):
    """Return all non-deleted dishes."""

    items, next_cursor, has_next = crud.get_paginated_dishes(
        current_user.id, db, params
    )

    return Page(items=items, next_cursor=next_cursor, has_next=has_next)


@router.get(
    "/{dish_id}",
    response_model=schemas.DishOut,
    name=RouteName.DISH_DETAIL,
    response_model_by_alias=False,
)
def read_one_dish(
    dish_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
):
    """Return a single dish by id. Raises 404 if not found or deleted."""

    dish = crud.get_one_dish(dish_id, current_user.id, db)
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    return dish


@router.post(
    "/",
    response_model=schemas.DishOut,
    name=RouteName.DISH_CREATE,
    response_model_by_alias=False,
)
def create_dish(
    dish: schemas.DishCreate,
    db: DbSession,
    current_user: CurrentUser,
):
    """Create a new dish linked to an existing ingredient. Raises 404 if ingredient not found."""

    new_dish = crud.create_dish(dish, current_user.id, db)
    if not new_dish:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    db.commit()

    return new_dish


@router.patch(
    "/{dish_id}",
    response_model=schemas.DishOut,
    name=RouteName.DISH_UPDATE,
    response_model_by_alias=False,
)
def update_dish(
    dish_id: uuid.UUID,
    dish_update: schemas.DishUpdate,
    db: DbSession,
    current_user: CurrentUser,
):
    """Update one or more fields of an existing dish. Raises 404 if not found."""

    dish = crud.update_dish(dish_id, current_user.id, dish_update, db)
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")

    db.commit()

    return dish


@router.delete(
    "/{dish_id}",
    name=RouteName.DISH_DELETE,
    response_model_by_alias=False,
)
def delete_dish(
    dish_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
):
    """Mark a dish as deleted. Raises 404 if not found."""

    dish = crud.delete_dish(dish_id, current_user.id, db)
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")

    db.commit()

    return {"status": "Dish marked as deleted"}
