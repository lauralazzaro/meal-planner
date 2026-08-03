from pydantic import BaseModel, Field
from app.core.schemas import PublicIdSchema
from app.core.enums import ShoppingCategory


class IngredientBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    shopping_category: ShoppingCategory | None = None


class IngredientCreate(IngredientBase):
    pass


class IngredientOut(IngredientBase, PublicIdSchema):
    pass


class IngredientUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    shopping_category: ShoppingCategory | None = None
