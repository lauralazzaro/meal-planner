from sqlalchemy.orm import Session
from app.shopping_list import models, schemas
from app.ingredients.models import Ingredient
from app.core.crud_helpers import (
    get_owned_record,
    get_owned_paginated_records,
)
import uuid


def create_shopping_list(
    shopping_list: schemas.ShoppingListCreate, user_id: int, db: Session
):
    """Create a new, empty shopping list."""
    new_list = models.ShoppingList(name=shopping_list.name, user_id=user_id)
    db.add(new_list)
    db.commit()
    db.refresh(new_list)
    return new_list


def get_paginated_shopping_list(user_id, db, params):
    return get_owned_paginated_records(
        models.ShoppingList, user_id, db, params, sort_field="id"
    )


def get_shopping_list(shopping_list_public_id: uuid.UUID, user_id: int, db: Session):
    """Return a single shopping list by public_id."""
    return get_owned_record(
        models.ShoppingList,
        shopping_list_public_id,
        user_id,
        db,
        True,
        lookup_field="public_id",
    )


def update_shopping_list(
    shopping_list_public_id: uuid.UUID,
    payload: schemas.ShoppingListUpdate,
    user_id: int,
    db: Session,
):
    """Update fields of an existing shopping list (e.g. its name)."""
    shopping_list = get_shopping_list(shopping_list_public_id, user_id, db)
    if not shopping_list:
        return None

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(shopping_list, field, value)

    db.commit()
    db.refresh(shopping_list)
    return shopping_list


def delete_shopping_list(shopping_list_public_id: uuid.UUID, user_id: int, db: Session):
    """Permanently delete a shopping list and all its items (cascade)."""
    shopping_list = get_shopping_list(shopping_list_public_id, user_id, db)
    if not shopping_list:
        return None

    db.delete(shopping_list)
    db.commit()
    return shopping_list


def create_shopping_list_item(
    shopping_list_public_id: uuid.UUID,
    item: schemas.ShoppingListItemCreate,
    user_id: int,
    db: Session,
):
    """Add an item to an existing shopping list, either linked to an
    ingredient or as free text. Returns None if the shopping list or
    the referenced ingredient don't exist."""

    shopping_list = get_shopping_list(shopping_list_public_id, user_id, db)
    if not shopping_list:
        return None

    if item.ingredient_public_id is not None:
        ingredient = (
            db.query(Ingredient)
            .filter(
                Ingredient.public_id == item.ingredient_public_id,
                Ingredient.user_id == user_id,
                Ingredient.is_deleted == False,
            )
            .first()
        )
        if not ingredient:
            return None

        new_item = models.ShoppingListItem(
            shopping_list_id=shopping_list.id,
            ingredient_id=ingredient.id,
            name=ingredient.name,
            shopping_category=ingredient.shopping_category,
            quantity=item.quantity,
            unit=item.unit,
        )
    else:
        new_item = models.ShoppingListItem(
            shopping_list_id=shopping_list.id,
            name=item.name,
            shopping_category=item.shopping_category,
            quantity=item.quantity,
            unit=item.unit,
        )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


def get_owned_shopping_list_item(
    shopping_list_public_id: uuid.UUID, item_id: int, user_id: int, db: Session
):
    """Return a shopping list item, verifying it belongs to a list owned by the user."""
    return (
        db.query(models.ShoppingListItem)
        .join(models.ShoppingList)
        .filter(
            models.ShoppingListItem.id == item_id,
            models.ShoppingList.public_id == shopping_list_public_id,
            models.ShoppingList.user_id == user_id,
        )
        .first()
    )


def update_shopping_list_item(
    shopping_list_public_id: uuid.UUID,
    item_id: int,
    payload: schemas.ShoppingListItemUpdate,
    user_id: int,
    db: Session,
):
    """Update quantity, unit, or checked status of a shopping list item."""
    item = get_owned_shopping_list_item(shopping_list_public_id, item_id, user_id, db)
    if not item:
        return None

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item


def delete_shopping_list_item(
    shopping_list_public_id: uuid.UUID, item_id: int, user_id: int, db: Session
):
    """Permanently remove a single item from a shopping list."""
    item = get_owned_shopping_list_item(shopping_list_public_id, item_id, user_id, db)
    if not item:
        return None

    db.delete(item)
    db.commit()
    return item
