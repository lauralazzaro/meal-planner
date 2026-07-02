from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.weekly_plans import crud, schemas

router = APIRouter(prefix="/weeklyplans", tags=["weeklyplans"])


@router.get("/", response_model=list[schemas.WeeklyPlanOut])
def read_all_weekly_plans(db: Session = Depends(get_db)):
    """Return all weekly plans."""

    return crud.get_all_weekly_plans(db)
