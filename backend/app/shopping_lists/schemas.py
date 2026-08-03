import uuid
from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from app.core.schemas import PublicIdSchema, ORMSchema
from app.core.enums import ShoppingCategory


class ShoppingListItemCreate(BaseModel):
    ingredient_public_id: uuid.UUID | None = None
    name: str | None = Field(None, min_length=1, max_length=100)
    shopping_category: ShoppingCategory | None = None
    quantity: float | None = Field(None, gt=0)
    unit: str | None = Field(None, max_length=20)

    @model_validator(mode="after")
    def check_ingredient_or_freetext(self):
        if self.ingredient_public_id is None:
            if not self.name or not self.shopping_category:
                raise ValueError(
                    "Provide either ingredient_public_id, or both name and shopping_category."
                )
        return self


class ShoppingListItemOut(ORMSchema):
    id: int
    name: str
    shopping_category: ShoppingCategory | None = None
    quantity: float | None = None
    unit: str | None = None
    is_checked: bool
    ingredient_id: uuid.UUID | None = Field(None, alias="ingredient_public_id")


class ShoppingListItemUpdate(BaseModel):
    quantity: float | None = Field(None, gt=0)
    unit: str | None = Field(None, max_length=20)
    is_checked: bool | None = None


class ShoppingListCreate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)


class ShoppingListOut(PublicIdSchema):
    name: str | None = None
    created_at: datetime
    items: list[ShoppingListItemOut] = []


class ShoppingListUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
