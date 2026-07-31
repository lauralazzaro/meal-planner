from pydantic import BaseModel, Field
from app.dishes import schemas as dishes_schemas
from enum import Enum
import uuid
from app.core.schemas import PublicIdSchema, ORMSchema


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
