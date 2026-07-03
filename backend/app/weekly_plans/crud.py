from sqlalchemy.orm import Session
from app.weekly_plans import models, schemas


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


def add_weekly_plan(weekly_plan: schemas.WeeklyPlanCreate, db: Session):
    """Add new weekly plan in the system. Verify if new one is default and set the previous as not default"""

    if weekly_plan.is_default is True:
        db.query(models.WeeklyPlan).filter(models.WeeklyPlan.is_default == True).update(
            {"is_default": False}
        )

    new_weekly_plan = models.WeeklyPlan(**weekly_plan.model_dump())
    db.add(new_weekly_plan)
    db.commit()
    db.refresh(new_weekly_plan)
    return new_weekly_plan


def add_dishes_to_plan(
    plan_id: int, dishes_data: list[schemas.WeeklyPlanDishCreate], db: Session
):
    """Add multiple dishes to a weekly plan in a single transaction.
    Returns None if the plan doesn't exist or any dish_id is invalid."""

    plan = db.query(models.WeeklyPlan).filter(models.WeeklyPlan.id == plan_id).first()
    if not plan:
        return None

    dish_ids = [item.dish_id for item in dishes_data]
    existing_dishes = (
        db.query(models.Dish)
        .filter(models.Dish.id.in_(dish_ids), models.Dish.is_deleted == False)
        .all()
    )

    if len(existing_dishes) != len(set(dish_ids)):
        return None  # at least one dish_id is invalid

    new_entries = []
    for item in dishes_data:
        entry = models.WeeklyPlanDish(
            weekly_plan_id=plan_id,
            day_of_week=item.day_of_week,
            meal_type=item.meal_type,
            dish_id=item.dish_id,
        )
        db.add(entry)
        new_entries.append(entry)

    db.commit()
    for entry in new_entries:
        db.refresh(entry)

    return new_entries


def update_plan(plan_id: int, plan_update: schemas.WeeklyPlanUpdate, db: Session):
    """Update name or default status of a plan"""

    plan = db.query(models.WeeklyPlan).filter(models.WeeklyPlan.id == plan_id).first()

    if not plan:
        return None

    if plan_update.is_default is True:
        db.query(models.WeeklyPlan).filter(models.WeeklyPlan.is_default == True).update(
            {"is_default": False}
        )

    update_data = plan_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(plan, field, value)

    db.commit()
    db.refresh(plan)

    return plan


def delete_weekly_plan(plan_id: int, db: Session):
    """Permanently delete a weekly plan.

    Hard delete is used here (not soft delete) because a WeeklyPlan is
    purely organizational -- unlike Ingredient, nothing else depends on
    it, and there's no need to preserve history or allow recovery once
    it's deleted.
    """

    plan = db.query(models.WeeklyPlan).filter(models.WeeklyPlan.id == plan_id).first()
    if not plan:
        return None

    db.delete(plan)
    db.commit()
    return plan


def delete_weekly_plan_dish(plan_id: int, weekly_plan_dish_id: int, db: Session):
    """Delete a dish entry from a weekly plan"""

    weekly_dish = (
        db.query(models.WeeklyPlanDish)
        .filter(
            models.WeeklyPlanDish.weekly_plan_id == plan_id,
            models.WeeklyPlanDish.id == weekly_plan_dish_id,
        )
        .first()
    )
    if not weekly_dish:
        return None

    db.delete(weekly_dish)
    db.commit()

    return weekly_dish
