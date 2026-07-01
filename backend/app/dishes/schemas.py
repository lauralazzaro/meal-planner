from pydantic import BaseModel, model_validator
from app.ingredients import schemas as ing_schemas


class DishBase(BaseModel):
    label: str | None = None
    comment: str | None = None
    main_ingredient_id: int | None = None
    main_category: str | None = None


class DishOut(DishBase):
    id: int
    main_ingredient: ing_schemas.IngredientOut | None = None

    model_config = {"from_attributes": True}


class DishCreate(DishBase):
    @model_validator(mode="after")
    def check_main_reference(self):
        """Exactly one of main_ingredient_id or main_category must be set."""
        has_ingredient = self.main_ingredient_id is not None
        has_category = self.main_category is not None
        if has_ingredient == has_category:  # entrambi True o entrambi False
            raise ValueError(
                "Exactly one of main_ingredient_id or main_category must be provided."
            )
        return self


class DishUpdate(BaseModel):
    label: str | None = None
    comment: str | None = None
    main_ingredient_id: int | None = None
    main_category: str | None = None
