from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.ingredients.router import router as ingredients_router
from app.dishes.router import router as dishes_router
from app.weekly_plans.router import router as weekly_plans_router
from app.shopping_lists.router import router as shopping_lists_router
from app.auth.router import router as auth_router

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingredients_router, prefix=settings.API_V1_STR)
app.include_router(dishes_router, prefix=settings.API_V1_STR)
app.include_router(weekly_plans_router, prefix=settings.API_V1_STR)
app.include_router(shopping_lists_router, prefix=settings.API_V1_STR)
app.include_router(auth_router, prefix=settings.API_V1_STR)


@app.get("/")
def read_root():
    """Simple health-check endpoint to verify the API is running."""
    return {"status": "Meal Planner backend is running"}
