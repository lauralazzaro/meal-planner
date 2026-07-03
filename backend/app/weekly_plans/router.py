from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.weekly_plans import crud, schemas

router = APIRouter(prefix="/weeklyplans", tags=["weeklyplans"])


@router.get("/", response_model=list[schemas.WeeklyPlanOut])
def read_all_weekly_plans(db: Session = Depends(get_db)):
    """Return all weekly plans."""

    return crud.get_all_weekly_plans(db)


@router.post("/", response_model=schemas.WeeklyPlanOut)
def add_weekly_plan(
    weekly_plan: schemas.WeeklyPlanCreate, db: Session = Depends(get_db)
):
    return crud.create_weekly_plan(weekly_plan, db)


@router.post("/{plan_id}/dishes", response_model=list[schemas.WeeklyPlanDishOut])
def add_dishes_to_plan(
    plan_id: int,
    payload: schemas.WeeklyPlanDishBulkCreate,
    db: Session = Depends(get_db),
):
    """Add multiple dishes to a weekly plan at once. Fails entirely if any dish_id is invalid."""

    entries = crud.add_dishes_to_plan(plan_id, payload.dishes, db)
    if entries is None:
        raise HTTPException(
            status_code=404, detail="Plan not found or one or more dish_id invalid"
        )
    return entries


@router.patch("/{plan_id}", response_model=schemas.WeeklyPlanOut)
def update_plan(
    plan_id: int, plan_update: schemas.WeeklyPlanUpdate, db: Session = Depends(get_db)
):
    """Update a name or default status of a plan"""

    updated_plan = crud.update_plan(plan_id, plan_update, db)

    if not updated_plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    return updated_plan


@router.delete("/{plan_id}")
def delete_weekly_plan(plan_id: int, db: Session = Depends(get_db)):
    """Permanently delete a weekly plan."""

    plan = crud.delete_weekly_plan(plan_id, db)

    if not plan:
        raise HTTPException(status_code=404, detail="Weekly plan not found")

    return {"status": "Weekly plan deleted"}
