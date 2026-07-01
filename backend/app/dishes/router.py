from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dishes import crud, schemas

router = APIRouter(prefix="/dishes", tags=["dishes"])


@router.get("/", response_model=list[schemas.DishOut])
def get_all_dishes(db: Session = Depends(get_db)):
    """Return all non-deleted dishes, including their ingredients."""
    return crud.get_all_dishes(db)
