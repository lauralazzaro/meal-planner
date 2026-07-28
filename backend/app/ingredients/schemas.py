import uuid

from pydantic import BaseModel, Field


class IngredientBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    shopping_category: str = Field(..., min_length=1, max_length=50)


class IngredientCreate(IngredientBase):
    pass


class IngredientOut(IngredientBase):
    id: uuid.UUID = Field(alias="public_id")
    model_config = {"from_attributes": True, "populate_by_name": True}


class IngredientUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    shopping_category: str | None = Field(None, min_length=1, max_length=50)
