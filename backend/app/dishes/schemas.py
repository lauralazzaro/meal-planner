from pydantic import BaseModel, Field
from app.ingredients import schemas as ing_schemas


class DishBase(BaseModel):
    label: str | None = Field(None, min_length=1, max_length=100)
    comment: str | None = Field(None, min_length=1, max_length=500)
    main_ingredient_id: int | None = Field(None, gt=0)


class DishCreate(DishBase):
    main_ingredient_id: int = Field(..., gt=0)


class DishOut(DishBase):
    id: int
    main_ingredient: ing_schemas.IngredientOut | None = None

    model_config = {"from_attributes": True}


class DishUpdate(BaseModel):
    label: str | None = Field(None, min_length=1, max_length=100)
    comment: str | None = Field(None, min_length=1, max_length=500)
    main_ingredient_id: int | None = Field(None, gt=0)
