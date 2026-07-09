from sqlalchemy.orm import Session
from app.shopping_list import models, schemas
from app.ingredients.models import Ingredient


def create_shopping_list(shopping_list: schemas.ShoppingListCreate, db: Session):
    """Create a new, empty shopping list."""
    new_list = models.ShoppingList(name=shopping_list.name)
    db.add(new_list)
    db.commit()
    db.refresh(new_list)
    return new_list


def get_all_shopping_lists(db: Session):
    """Return all shopping lists."""
    return db.query(models.ShoppingList).all()


def get_shopping_list(shopping_list_id: int, db: Session):
    """Return a single shopping list by id."""
    return (
        db.query(models.ShoppingList)
        .filter(models.ShoppingList.id == shopping_list_id)
        .first()
    )


def update_shopping_list(
    shopping_list_id: int, payload: schemas.ShoppingListUpdate, db: Session
):
    """Update fields of an existing shopping list (e.g. its name)."""
    shopping_list = get_shopping_list(shopping_list_id, db)
    if not shopping_list:
        return None

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(shopping_list, field, value)

    db.commit()
    db.refresh(shopping_list)
    return shopping_list


def delete_shopping_list(shopping_list_id: int, db: Session):
    """Permanently delete a shopping list and all its items (cascade)."""
    shopping_list = get_shopping_list(shopping_list_id, db)
    if not shopping_list:
        return None

    db.delete(shopping_list)
    db.commit()
    return shopping_list


def create_shopping_list_item(
    shopping_list_id: int, item: schemas.ShoppingListItemCreate, db: Session
):
    """Add an item to an existing shopping list, either linked to an
    ingredient or as free text. Returns None if the shopping list or
    the referenced ingredient don't exist."""

    shopping_list = get_shopping_list(shopping_list_id, db)
    if not shopping_list:
        return None

    if item.ingredient_id is not None:
        ingredient = (
            db.query(Ingredient)
            .filter(Ingredient.id == item.ingredient_id, Ingredient.is_deleted == False)
            .first()
        )
        if not ingredient:
            return None

        new_item = models.ShoppingListItem(
            shopping_list_id=shopping_list_id,
            ingredient_id=ingredient.id,
            name=ingredient.name,
            shopping_category=ingredient.shopping_category,
            quantity=item.quantity,
            unit=item.unit,
        )
    else:
        new_item = models.ShoppingListItem(
            shopping_list_id=shopping_list_id,
            name=item.name,
            shopping_category=item.shopping_category,
            quantity=item.quantity,
            unit=item.unit,
        )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


def update_shopping_list_item(
    shopping_list_id: int,
    item_id: int,
    payload: schemas.ShoppingListItemUpdate,
    db: Session,
):
    """Update quantity, unit, or checked status of a shopping list item."""
    item = (
        db.query(models.ShoppingListItem)
        .filter(
            models.ShoppingListItem.id == item_id,
            models.ShoppingListItem.shopping_list_id == shopping_list_id,
        )
        .first()
    )
    if not item:
        return None

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item


def delete_shopping_list_item(shopping_list_id: int, item_id: int, db: Session):
    """Permanently remove a single item from a shopping list."""
    item = (
        db.query(models.ShoppingListItem)
        .filter(
            models.ShoppingListItem.id == item_id,
            models.ShoppingListItem.shopping_list_id == shopping_list_id,
        )
        .first()
    )
    if not item:
        return None

    db.delete(item)
    db.commit()
    return item
