import json
import os
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.ingredients.models import Ingredient


def load_json(filename: str):
    """Load seed data from a JSON file."""
    filepath = os.path.join(os.path.dirname(__file__), filename)
    with open(filepath) as f:
        return json.load(f)


def seed_ingredients(db: Session):
    """Insert ingredients if they don't already exist."""
    data = load_json("ingredients.json")
    print(f"Loaded {len(data)} items from JSON")
    count = 0
    for item in data:
        exists = db.query(Ingredient).filter(Ingredient.name == item["name"]).first()
        if not exists:
            db.add(Ingredient(**item))
            count += 1
    db.commit()
    print(f"Inserted {count} new ingredients.")


print(f"__name__ is: {__name__}")


def run():
    db = SessionLocal()
    try:
        seed_ingredients(db)
    except Exception as e:
        print(f"Seed failed: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    run()
