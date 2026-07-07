from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.shopping_list import crud, schemas

router = APIRouter(prefix="/shopping-lists", tags=["shopping-lists"])
