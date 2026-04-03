from fastapi import APIRouter, Response
from fastapi.params import Depends
from sqlalchemy.orm import Session
from db import get_db
from modules.users.schemas import UserCreate
from modules.users.services import add_user
from shared.utils import validation_error


router = APIRouter()

@router.post("/")
def create_user(payload: UserCreate, response: Response, db: Session = Depends(get_db)):
    user = add_user(payload, db)

    if user:
        response.status_code = 201
        return {
            'message': 'User created successfully.',
            'data': user,
        }
    
    return validation_error('user', 'Failed to create user.', status=500)

