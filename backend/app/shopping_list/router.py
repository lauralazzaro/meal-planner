from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.shopping_list import crud, schemas

router = APIRouter(prefix="/shopping-lists", tags=["shopping-lists"])


@router.get("/", response_model=list[schemas.ShoppingListOut])
def read_all_shopping_lists(db: Session = Depends(get_db)):
    """Return all shopping lists."""

    return crud.get_all_shopping_lists(db)


@router.get("/{list_id}", response_model=schemas.ShoppingListOut)
def read_all_shopping_lists(list_id: int, db: Session = Depends(get_db)):
    """Return one shopping list."""

    return crud.get_shopping_list(list_id, db)


@router.post("/", response_model=schemas.ShoppingListOut)
def add_shopping_list(list: schemas.ShoppingListCreate, db: Session = Depends(get_db)):
    return crud.create_shopping_list(list, db)


@router.post("/{list_id}/item", response_model=schemas.ShoppingListItemOut)
def add_dishes_to_plan(
    list_id: int,
    item: schemas.ShoppingListItemCreate,
    db: Session = Depends(get_db),
):
    """Add multiple dishes to a weekly plan at once. Fails entirely if any dish_id is invalid."""

    added_item = crud.create_shopping_list_item(list_id, item, db)
    if added_item is None:
        raise HTTPException(
            status_code=404, detail="List not found or ingredients invalid"
        )
    return added_item
