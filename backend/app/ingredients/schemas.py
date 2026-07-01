from pydantic import BaseModel


class IngredientBase(BaseModel):
    name: str
    shopping_category: str


class IngredientCreate(IngredientBase):
    pass


class IngredientOut(IngredientBase):
    id: int

    model_config = {"from_attributes": True}


class IngredientUpdate(BaseModel):
    name: str | None = None
    shopping_category: str | None = None
