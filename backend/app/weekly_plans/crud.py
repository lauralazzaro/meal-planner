from sqlalchemy.orm import Session
from app.weekly_plans import models, schemas


# get one
def get_one_weekly_plan(weekly_plan_id: int, db: Session):
    """Return a single weekly plan."""

    return (
        db.query(models.WeeklyPlan)
        .filter(models.WeeklyPlan.id == weekly_plan_id)
        .first()
    )


def get_default_weekly_plan(db: Session):
    """Return a single weekly plan."""

    return (
        db.query(models.WeeklyPlan).filter(models.WeeklyPlan.is_default == True).first()
    )


def get_all_weekly_plans(db: Session):
    return db.query(models.WeeklyPlan).all()


# get all
# create
# update
