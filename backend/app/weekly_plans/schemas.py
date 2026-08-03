import uuid

from pydantic import BaseModel, Field
from app.dishes import schemas as dishes_schemas
from app.core.schemas import PublicIdSchema, ORMSchema
from app.core.enums import DayOfWeek, MealType


class WeeklyPlanDishBase(BaseModel):
    day_of_week: DayOfWeek
    meal_type: MealType


class WeeklyPlanDishCreate(WeeklyPlanDishBase):
    dish_public_id: uuid.UUID


class WeeklyPlanDishOut(WeeklyPlanDishBase, ORMSchema):
    id: int
    dish: dishes_schemas.DishOut


class WeeklyPlanDishUpdate(BaseModel):
    day_of_week: DayOfWeek | None = None
    meal_type: MealType | None = None
    dish_public_id: uuid.UUID | None = None


class WeeklyPlanDishBulkCreate(BaseModel):
    dishes: list[WeeklyPlanDishCreate]


class WeeklyPlanBase(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50)
    is_default: bool = False


class WeeklyPlanCreate(WeeklyPlanBase):
    pass


class WeeklyPlanOut(WeeklyPlanBase, PublicIdSchema):
    dishes: list[WeeklyPlanDishOut] | None = None


class WeeklyPlanUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50)
    is_default: bool | None = None
