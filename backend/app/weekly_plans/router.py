from fastapi import APIRouter, HTTPException, Request, Response, status
from app.weekly_plans import crud, schemas
from app.auth.models import User
from app.core.dependencies import DbSession, CurrentUser
from app.core.route_names import RouteName
from app.core.pagination import Page, PaginationQuery
import uuid

router = APIRouter(prefix="/weekly-plans", tags=["weekly-plans"])


@router.get(
    "/",
    response_model=Page[schemas.WeeklyPlanOut],
    name=RouteName.WEEKLY_PLAN_LIST,
    response_model_by_alias=False,
)
def read_all_weekly_plans(
    db: DbSession,
    current_user: CurrentUser,
    params: PaginationQuery,
):
    """Return all weekly plans."""

    items, next_cursor, has_next = crud.get_paginated_plans(current_user.id, db, params)
    return Page(items=items, next_cursor=next_cursor, has_next=has_next)


@router.get(
    "/{plan_id}",
    response_model=schemas.WeeklyPlanOut,
    name=RouteName.WEEKLY_PLAN_DETAIL,
    response_model_by_alias=False,
)
def read_one_plan_by_id(
    plan_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
):
    """Return one weekly plan."""

    plan = crud.get_one_weekly_plan(plan_id, current_user.id, db)

    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    return plan


@router.post(
    "/",
    response_model=schemas.WeeklyPlanOut,
    status_code=status.HTTP_201_CREATED,
    name=RouteName.WEEKLY_PLAN_CREATE,
    response_model_by_alias=False,
)
def add_weekly_plan(
    weekly_plan: schemas.WeeklyPlanCreate,
    response: Response,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
):
    new_weekly_plan = crud.create_weekly_plan(weekly_plan, current_user.id, db)
    db.commit()
    response.headers["Location"] = str(
        request.url_for(RouteName.WEEKLY_PLAN_DETAIL, plan_id=new_weekly_plan.public_id)
    )
    return new_weekly_plan


@router.patch(
    "/{plan_id}",
    response_model=schemas.WeeklyPlanOut,
    name=RouteName.WEEKLY_PLAN_UPDATE,
    response_model_by_alias=False,
)
def update_plan(
    plan_id: uuid.UUID,
    plan_update: schemas.WeeklyPlanUpdate,
    db: DbSession,
    current_user: CurrentUser,
):
    """Update a name or default status of a plan"""

    updated_plan = crud.update_plan(plan_id, plan_update, current_user.id, db)

    if not updated_plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    db.commit()

    return updated_plan


@router.delete(
    "/{plan_id}",
    name=RouteName.WEEKLY_PLAN_DELETE,
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_weekly_plan(
    plan_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
):
    """Permanently delete a weekly plan."""

    plan = crud.delete_weekly_plan(plan_id, current_user.id, db)

    if not plan:
        raise HTTPException(status_code=404, detail="Weekly plan not found")

    db.commit()


@router.post(
    "/{plan_id}/dishes",
    response_model=list[schemas.WeeklyPlanDishOut],
    status_code=status.HTTP_201_CREATED,
    name=RouteName.WEEKLY_PLAN_ADD_DISHES,
)
def add_dishes_to_plan(
    plan_id: uuid.UUID,
    payload: schemas.WeeklyPlanDishBulkCreate,
    db: DbSession,
    current_user: CurrentUser,
):
    """Add multiple dishes to a weekly plan at once. Fails entirely if any dish_id is invalid."""

    entries = crud.add_dishes_to_plan(plan_id, payload.dishes, current_user.id, db)
    if entries is None:
        raise HTTPException(
            status_code=404, detail="Plan not found or one or more dish_id invalid"
        )

    db.commit()

    return entries


@router.delete(
    "/{plan_id}/dishes/{weekly_plan_dish_id}",
    name=RouteName.WEEKLY_PLAN_DELETE_DISH,
    status_code=status.HTTP_204_NO_CONTENT,
    response_model_by_alias=False,
)
def delete_dish_from_plan(
    plan_id: uuid.UUID,
    weekly_plan_dish_id: int,
    db: DbSession,
    current_user: CurrentUser,
):
    """Delete one dish entry from a weekly list"""

    weekly_plan_dish = crud.delete_weekly_plan_dish(
        plan_id, weekly_plan_dish_id, current_user.id, db
    )

    if not weekly_plan_dish:
        raise HTTPException(status_code=404, detail="Weekly plan dish entry not found")

    db.commit()
