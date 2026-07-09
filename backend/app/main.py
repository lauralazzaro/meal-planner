from fastapi import FastAPI
from app.ingredients.router import router as ingredients_router
from app.dishes.router import router as dishes_router
from app.weekly_plans.router import router as weekly_plans_router
from app.shopping_list.router import router as shopping_lists
from app.auth.router import router as auth_router

app = FastAPI()

app.include_router(ingredients_router)
app.include_router(dishes_router)
app.include_router(weekly_plans_router)
app.include_router(shopping_lists)
app.include_router(auth_router)


@app.get("/")
def read_root():
    """Simple health-check endpoint to verify the API is running."""

    return {"status": "LiteMind backend is running"}
