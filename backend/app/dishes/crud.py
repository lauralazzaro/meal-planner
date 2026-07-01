from sqlalchemy.orm import Session
from app.dishes import models, schemas

def get_all_dishes(db: Session):
    return db.query(models.Dish).filter(models.Dish.is_deleted == False).all()