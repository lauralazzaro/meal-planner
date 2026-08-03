from pydantic import BaseModel, Field
from app.ingredients import schemas as ing_schemas
import uuid
from app.core.schemas import PublicIdSchema


class DishBase(BaseModel):
    label: str | None = Field(None, min_length=1, max_length=100)
    comment: str | None = Field(None, min_length=1, max_length=500)


class DishCreate(DishBase):
    main_ingredient_public_id: uuid.UUID


class DishOut(DishBase, PublicIdSchema):
    main_ingredient: ing_schemas.IngredientOut | None = None


class DishUpdate(BaseModel):
    label: str | None = Field(None, min_length=1, max_length=100)
    comment: str | None = Field(None, min_length=1, max_length=500)
    main_ingredient_public_id: uuid.UUID | None = None
