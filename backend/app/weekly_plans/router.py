from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.weekly_plans import crud, schemas
from app.auth.models import User
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/weekly-plans", tags=["weekly-plans"])


@router.get("/", response_model=list[schemas.WeeklyPlanOut])
def read_all_weekly_plans(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Return all weekly plans."""

    return crud.get_all_weekly_plans(current_user.id, db)


@router.get("/{plan_id}", response_model=schemas.WeeklyPlanOut)
def read_one_plan_by_id(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return one weekly plan."""

    plan = crud.get_one_weekly_plan(plan_id, current_user.id, db)

    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    return plan


@router.post("/", response_model=schemas.WeeklyPlanOut)
def add_weekly_plan(
    weekly_plan: schemas.WeeklyPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.create_weekly_plan(weekly_plan, current_user.id, db)


@router.patch("/{plan_id}", response_model=schemas.WeeklyPlanOut)
def update_plan(
    plan_id: int,
    plan_update: schemas.WeeklyPlanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a name or default status of a plan"""

    updated_plan = crud.update_plan(plan_id, plan_update, current_user.id, db)

    if not updated_plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    return updated_plan


@router.delete("/{plan_id}")
def delete_weekly_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Permanently delete a weekly plan."""

    plan = crud.delete_weekly_plan(plan_id, current_user.id, db)

    if not plan:
        raise HTTPException(status_code=404, detail="Weekly plan not found")

    return {"status": "Weekly plan deleted"}


@router.post("/{plan_id}/dishes", response_model=list[schemas.WeeklyPlanDishOut])
def add_dishes_to_plan(
    plan_id: int,
    payload: schemas.WeeklyPlanDishBulkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add multiple dishes to a weekly plan at once. Fails entirely if any dish_id is invalid."""

    entries = crud.add_dishes_to_plan(plan_id, payload.dishes, current_user.id, db)
    if entries is None:
        raise HTTPException(
            status_code=404, detail="Plan not found or one or more dish_id invalid"
        )
    return entries


@router.delete("/{plan_id}/dishes/{weekly_plan_dish_id}")
def delete_dish_from_plan(
    plan_id: int,
    weekly_plan_dish_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete one dish entry from a weekly list"""

    weekly_plan_dish = crud.delete_weekly_plan_dish(
        plan_id, weekly_plan_dish_id, current_user.id, db
    )

    if not weekly_plan_dish:
        raise HTTPException(status_code=404, detail="Weekly plan dish entry not found")

    return {"status": "Weekly plan dish entry deleted"}
