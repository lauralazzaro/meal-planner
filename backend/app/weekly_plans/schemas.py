from pydantic import BaseModel
from app.dishes import schemas as dishes_schemas


class WeeklyPlanDishBase(BaseModel):
    day_of_week: str
    meal_type: str
    dish_id: int


class WeeklyPlanDishCreate(WeeklyPlanDishBase):
    pass


class WeeklyPlanDishOut(WeeklyPlanDishBase):
    id: int
    weekly_plan_id: int
    dish: dishes_schemas.DishOut

    model_config = {"from_attributes": True}


class WeeklyPlanDishUpdate(BaseModel):
    day_of_week: str | None = None
    meal_type: str | None = None
    dish_id: int | None = None


class WeeklyPlanDishBulkCreate(BaseModel):
    dishes: list[WeeklyPlanDishCreate]


class WeeklyPlanBase(BaseModel):
    name: str | None = None
    is_default: bool = False


class WeeklyPlanCreate(WeeklyPlanBase):
    pass


class WeeklyPlanOut(WeeklyPlanBase):
    id: int
    dishes: list[WeeklyPlanDishOut] | None = None

    model_config = {"from_attributes": True}


class WeeklyPlanUpdate(BaseModel):
    name: str | None = None
    is_default: bool | None = None
