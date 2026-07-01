from fastapi import FastAPI
from app.ingredients.router import router as ingredients_router
from app.dishes.router import router as dishes_router

app = FastAPI()

app.include_router(ingredients_router)
app.include_router(dishes_router)


@app.get("/")
def read_root():
    """Simple health-check endpoint to verify the API is running."""

    return {"status": "LiteMind backend is running"}
