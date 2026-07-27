from pydantic import BaseModel, Field
from app.ingredients import schemas as ing_schemas
import uuid


class DishBase(BaseModel):
    label: str | None = Field(None, min_length=1, max_length=100)
    comment: str | None = Field(None, min_length=1, max_length=500)


class DishCreate(DishBase):
    main_ingredient_public_id: uuid.UUID


class DishOut(DishBase):
    id: uuid.UUID = Field(alias="public_id")
    main_ingredient: ing_schemas.IngredientOut | None = None

    model_config = {"from_attributes": True, "populate_by_name": True}


class DishUpdate(BaseModel):
    label: str | None = Field(None, min_length=1, max_length=100)
    comment: str | None = Field(None, min_length=1, max_length=500)
    main_ingredient_public_id: uuid.UUID | None = None
