from pydantic import BaseModel, model_validator
from app.ingredients import schemas as ing_schemas


class DishBase(BaseModel):
    label: str | None = None
    comment: str | None = None
    main_ingredient_id: int


class DishCreate(DishBase):
    pass


class DishOut(DishBase):
    id: int
    main_ingredient: ing_schemas.IngredientOut | None = None

    model_config = {"from_attributes": True}


class DishUpdate(BaseModel):
    label: str | None = None
    comment: str | None = None
    main_ingredient_id: int | None = None
