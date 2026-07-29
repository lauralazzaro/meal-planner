import uuid

from app.core.pagination import Page, PaginationParams, pagination_params
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.ingredients import crud, schemas
from app.auth.models import User
from app.core.dependencies import get_current_user
from app.core.route_names import RouteName

router = APIRouter(prefix="/ingredients", tags=["ingredients"])


@router.get(
    "/",
    response_model=Page[schemas.IngredientOut],
    name=RouteName.INGREDIENT_LIST,
    response_model_by_alias=False,
)
def read_all_ingredients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    params: PaginationParams = Depends(pagination_params),
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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


@router.patch(
    "/{ingredient_id}",
    response_model=schemas.IngredientOut,
    name=RouteName.INGREDIENT_UPDATE,
    response_model_by_alias=False,
)
def update_ingredient(
    ingredient_id: uuid.UUID,
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


@router.delete(
    "/{ingredient_id}",
    name=RouteName.INGREDIENT_DELETE,
    response_model_by_alias=False,
)
def delete_ingredient(
    ingredient_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark an ingredient as deleted."""
    ingredient = crud.delete_ingredient(ingredient_id, current_user.id, db)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return {"status": "Ingredient marked as deleted"}
