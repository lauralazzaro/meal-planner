import uuid

from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError

from app.core.dependencies import CurrentUser, DbSession
from app.core.pagination import Page, PaginationQuery
from app.core.route_names import RouteName
from app.ingredients import crud, schemas

router = APIRouter(prefix="/ingredients", tags=["ingredients"])


@router.get(
    "/",
    response_model=Page[schemas.IngredientOut],
    name=RouteName.INGREDIENT_LIST,
    response_model_by_alias=False,
)
def read_all_ingredients(
    db: DbSession,
    current_user: CurrentUser,
    params: PaginationQuery,
):
    """Return all ingredients owned by the current user."""
    items, next_cursor, has_next = crud.get_paginated_ingredients(
        current_user.id, db, params
    )
    return Page(items=items, next_cursor=next_cursor, has_next=has_next)


@router.get(
    "/{ingredient_id}",
    response_model=schemas.IngredientOut,
    name=RouteName.INGREDIENT_DETAIL,
    response_model_by_alias=False,
)
def read_ingredient(
    ingredient_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
):
    """Return a single ingredient by id, owned by the current user."""
    ingredient = crud.get_ingredient(ingredient_id, current_user.id, db)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient


@router.post(
    "/",
    response_model=schemas.IngredientOut,
    name=RouteName.INGREDIENT_CREATE,
    response_model_by_alias=False,
)
def create_ingredient(
    ingredient: schemas.IngredientCreate,
    db: DbSession,
    current_user: CurrentUser,
):
    """Add a new ingredient to the pool."""
    try:
        new_ingredient = crud.create_ingredient(ingredient, current_user.id, db)
        db.commit()
        return new_ingredient
    except IntegrityError:
        raise HTTPException(
            status_code=409, detail="An ingredient with this name already exists"
        )


@router.patch(
    "/{ingredient_id}",
    response_model=schemas.IngredientOut,
    name=RouteName.INGREDIENT_UPDATE,
    response_model_by_alias=False,
)
def update_ingredient(
    ingredient_id: uuid.UUID,
    ingredient_update: schemas.IngredientUpdate,
    db: DbSession,
    current_user: CurrentUser,
):
    """Update one or more fields of an existing ingredient."""
    ingredient = crud.update_ingredient(
        ingredient_id, current_user.id, ingredient_update, db
    )
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    db.commit()
    return ingredient


@router.delete(
    "/{ingredient_id}",
    name=RouteName.INGREDIENT_DELETE,
    response_model_by_alias=False,
)
def delete_ingredient(
    ingredient_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
):
    """Mark an ingredient as deleted."""
    ingredient = crud.delete_ingredient(ingredient_id, current_user.id, db)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    db.commit()
    return {"status": "Ingredient marked as deleted"}
