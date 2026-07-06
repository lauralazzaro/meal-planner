from pydantic import BaseModel, Field
from app.dishes import schemas as dishes_schemas
from enum import Enum


class DayOfWeek(str, Enum):
    lunedi = "lunedì"
    martedi = "martedì"
    mercoledi = "mercoledì"
    giovedi = "giovedì"
    venerdi = "venerdì"
    sabato = "sabato"
    domenica = "domenica"


class MealType(str, Enum):
    colazione = "colazione"
    pranzo = "pranzo"
    cena = "cena"


class WeeklyPlanDishBase(BaseModel):
    day_of_week: DayOfWeek
    meal_type: MealType
    dish_id: int = Field(..., gt=0)


class WeeklyPlanDishCreate(WeeklyPlanDishBase):
    pass


class WeeklyPlanDishOut(WeeklyPlanDishBase):
    id: int
    weekly_plan_id: int
    dish: dishes_schemas.DishOut

    model_config = {"from_attributes": True}


class WeeklyPlanDishUpdate(BaseModel):
    day_of_week: DayOfWeek | None = None
    meal_type: MealType | None = None
    dish_id: int | None = Field(None, gt=0)


class WeeklyPlanDishBulkCreate(BaseModel):
    dishes: list[WeeklyPlanDishCreate]


class WeeklyPlanBase(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50)
    is_default: bool = False


class WeeklyPlanCreate(WeeklyPlanBase):
    pass


class WeeklyPlanOut(WeeklyPlanBase):
    id: int
    dishes: list[WeeklyPlanDishOut] | None = None

    model_config = {"from_attributes": True}


class WeeklyPlanUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50)
    is_default: bool | None = None
