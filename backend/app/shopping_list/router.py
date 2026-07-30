from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.shopping_list import crud, schemas
from app.auth.models import User
from app.core.dependencies import get_current_user
from app.core.route_names import RouteName
from app.core.pagination import Page, PaginationParams, pagination_params
import uuid

router = APIRouter(prefix="/shopping-lists", tags=["shopping-lists"])


@router.get(
    "/",
    response_model=Page[schemas.ShoppingListOut],
    name=RouteName.SHOPPING_LIST_LIST,
    response_model_by_alias=False,
)
def read_all_shopping_lists(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    params: PaginationParams = Depends(pagination_params),
):
    """Return all shopping lists."""

    items, next_cursor, has_next = crud.get_paginated_shopping_list(
        current_user.id, db, params
    )
    return Page(items=items, next_cursor=next_cursor, has_next=has_next)


@router.get(
    "/{list_id}",
    response_model=schemas.ShoppingListOut,
    name=RouteName.SHOPPING_LIST_DETAIL,
    response_model_by_alias=False,
)
def read_one_shopping_list(
    list_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return one shopping list."""

    shopping_list = crud.get_shopping_list(list_id, current_user.id, db)
    if not shopping_list:
        raise HTTPException(status_code=404, detail="Shopping list not found")
    return shopping_list


@router.post(
    "/",
    response_model=schemas.ShoppingListOut,
    name=RouteName.SHOPPING_LIST_CREATE,
    response_model_by_alias=False,
)
def add_shopping_list(
    shopping_list: schemas.ShoppingListCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create an empty shoppting list"""

    return crud.create_shopping_list(shopping_list, current_user.id, db)


@router.post(
    "/{list_id}/items",
    response_model=schemas.ShoppingListItemOut,
    name=RouteName.SHOPPING_LIST_ADD_ITEM,
    response_model_by_alias=False,
)
def add_item_to_shopping_list(
    list_id: uuid.UUID,
    item: schemas.ShoppingListItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add items to shopping list"""

    added_item = crud.create_shopping_list_item(list_id, item, current_user.id, db)
    if added_item is None:
        raise HTTPException(
            status_code=404, detail="List not found or ingredients invalid"
        )
    return added_item


@router.patch(
    "/{list_id}",
    response_model=schemas.ShoppingListOut,
    name=RouteName.SHOPPING_LIST_UPDATE,
    response_model_by_alias=False,
)
def update_shopping_list(
    list_id: uuid.UUID,
    shopping_list: schemas.ShoppingListUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update shopping list"""

    updated_list = crud.update_shopping_list(
        list_id, shopping_list, current_user.id, db
    )
    if updated_list is None:
        raise HTTPException(status_code=404, detail="List not found")
    return updated_list


@router.delete(
    "/{list_id}",
    name=RouteName.SHOPPING_LIST_DELETE,
    response_model_by_alias=False,
)
def delete_shopping_list(
    list_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted_list = crud.delete_shopping_list(list_id, current_user.id, db)
    if not deleted_list:
        raise HTTPException(status_code=404, detail="List not found.")

    return {"status": "Shopping list deleted."}


@router.delete(
    "/{list_id}/items/{item_id}",
    name=RouteName.SHOPPING_LIST_DELETE_ITEM,
    response_model_by_alias=False,
)
def delete_item_from_list(
    list_id: uuid.UUID,
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete one item from a shopping list"""

    shopping_list_item = crud.delete_shopping_list_item(
        list_id, item_id, current_user.id, db
    )

    if not shopping_list_item:
        raise HTTPException(status_code=404, detail="Shopping list item not found")

    return {"status": "Item deleted from shopping list"}


@router.patch(
    "/{list_id}/items/{item_id}",
    response_model=schemas.ShoppingListItemOut,
    name=RouteName.SHOPPING_LIST_UPDATE_ITEM,
    response_model_by_alias=False,
)
def update_item_from_list(
    list_id: uuid.UUID,
    item_id: int,
    item: schemas.ShoppingListItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update one item in a shopping list"""

    updated_item = crud.update_shopping_list_item(
        list_id, item_id, item, current_user.id, db
    )
    if not updated_item:
        raise HTTPException(status_code=404, detail="Item not found")

    return updated_item
