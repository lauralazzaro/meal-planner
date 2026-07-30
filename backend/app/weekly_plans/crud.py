from sqlalchemy.orm import Session, selectinload
from app.weekly_plans import models, schemas
from app.dishes.models import Dish
from app.core.crud_helpers import (
    get_owned_record,
    get_owned_paginated_records,
)


def get_one_weekly_plan(weekly_plan_public_id, user_id: int, db: Session):
    """Return a single weekly plan."""
    return get_owned_record(
        models.WeeklyPlan,
        weekly_plan_public_id,
        user_id,
        db,
        True,
        lookup_field="public_id",
        options=[
            selectinload(models.WeeklyPlan.dishes)
            .selectinload(models.WeeklyPlanDish.dish)
            .selectinload(Dish.main_ingredient)
        ],
    )


def get_paginated_plans(user_id, db, params):
    return get_owned_paginated_records(
        models.WeeklyPlan,
        user_id,
        db,
        params,
        sort_field="id",
        options=[
            selectinload(models.WeeklyPlan.dishes)
            .selectinload(models.WeeklyPlanDish.dish)
            .selectinload(Dish.main_ingredient)
        ],
    )


def create_weekly_plan(
    weekly_plan: schemas.WeeklyPlanCreate, user_id: int, db: Session
):
    """Add new weekly plan in the system and link it to the current user. Verify if new one is default and set the previous as not default"""

    if weekly_plan.is_default is True:
        db.query(models.WeeklyPlan).filter(
            models.WeeklyPlan.is_default == True, models.WeeklyPlan.user_id == user_id
        ).update({"is_default": False})

    new_weekly_plan = models.WeeklyPlan(**weekly_plan.model_dump(), user_id=user_id)
    db.add(new_weekly_plan)
    db.commit()
    db.refresh(new_weekly_plan)
    return new_weekly_plan


def add_dishes_to_plan(
    plan_public_id,
    dishes_data: list[schemas.WeeklyPlanDishCreate],
    user_id: int,
    db: Session,
):
    """Add multiple dishes to a weekly plan in a single transaction.
    Returns None if the plan doesn't exist or any dish_public_id is invalid."""

    plan = (
        db.query(models.WeeklyPlan)
        .filter(
            models.WeeklyPlan.public_id == plan_public_id,
            models.WeeklyPlan.user_id == user_id,
        )
        .first()
    )
    if not plan:
        return None

    dish_public_ids = [item.dish_public_id for item in dishes_data]
    existing_dishes = (
        db.query(Dish)
        .filter(
            Dish.public_id.in_(dish_public_ids),
            Dish.user_id == user_id,
            Dish.is_deleted == False,
        )
        .all()
    )

    if len(existing_dishes) != len(set(dish_public_ids)):
        return None  # at least one dish_public_id is invalid

    # map public_id -> internal id, so we can build FK references below
    dish_by_public_id = {dish.public_id: dish.id for dish in existing_dishes}

    new_entries = []
    for item in dishes_data:
        entry = models.WeeklyPlanDish(
            weekly_plan_id=plan.id,
            day_of_week=item.day_of_week,
            meal_type=item.meal_type,
            dish_id=dish_by_public_id[item.dish_public_id],
        )
        db.add(entry)
        new_entries.append(entry)

    db.commit()
    for entry in new_entries:
        db.refresh(entry)

    return new_entries


def update_plan(
    plan_public_id, plan_update: schemas.WeeklyPlanUpdate, user_id: int, db: Session
):
    """Update name or default status of a plan."""

    plan = (
        db.query(models.WeeklyPlan)
        .filter(
            models.WeeklyPlan.public_id == plan_public_id,
            models.WeeklyPlan.user_id == user_id,
        )
        .first()
    )
    if not plan:
        return None

    update_data = plan_update.model_dump(exclude_unset=True)

    if update_data.get("is_default") is True:
        db.query(models.WeeklyPlan).filter(
            models.WeeklyPlan.is_default == True,
            models.WeeklyPlan.user_id == user_id,
            models.WeeklyPlan.id != plan.id,
        ).update({"is_default": False})

    for field, value in update_data.items():
        setattr(plan, field, value)

    db.commit()
    db.refresh(plan)
    return plan


def delete_weekly_plan(plan_public_id, user_id: int, db: Session):
    """Permanently delete a weekly plan.

    Hard delete is used here (not soft delete) because a WeeklyPlan is
    purely organizational -- unlike Ingredient, nothing else depends on
    it, and there's no need to preserve history or allow recovery once
    it's deleted.
    """
    plan = (
        db.query(models.WeeklyPlan)
        .filter(
            models.WeeklyPlan.public_id == plan_public_id,
            models.WeeklyPlan.user_id == user_id,
        )
        .first()
    )
    if not plan:
        return None

    db.delete(plan)
    db.commit()
    return plan


def delete_weekly_plan_dish(
    plan_public_id, weekly_plan_dish_id: int, user_id: int, db: Session
):
    """Delete a dish entry from a weekly plan owned by the user."""

    weekly_dish = (
        db.query(models.WeeklyPlanDish)
        .join(models.WeeklyPlan)
        .filter(
            models.WeeklyPlan.public_id == plan_public_id,
            models.WeeklyPlanDish.id == weekly_plan_dish_id,
            models.WeeklyPlan.user_id == user_id,
        )
        .first()
    )
    if not weekly_dish:
        return None

    db.delete(weekly_dish)
    db.commit()
    return weekly_dish
