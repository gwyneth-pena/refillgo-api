from fastapi import APIRouter, Response
from fastapi.params import Depends
from sqlalchemy.orm import Session

from db import get_db
from modules.users.schemas import UserCreate


router = APIRouter()

@router.post("/")
def create_user(payload: UserCreate, response: Response, db: Session = Depends(get_db)):
    return {"message": "User created successfully!"}