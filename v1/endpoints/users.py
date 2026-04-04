from config import FRONTEND_URL
from fastapi import APIRouter, Response
from fastapi.params import Depends
from shared.email import send_email
from sqlalchemy.orm import Session
from db import get_db
from modules.users.schemas import UserCreateSchema, UserLoginSchema
from modules.users.services import add_user, authenticate_user
from shared.utils import validation_error
from fastapi import BackgroundTasks


router = APIRouter()

@router.post("/")
def create_user(payload: UserCreateSchema, response: Response,  background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user = add_user(payload, db, response)

    if user:
        background_tasks.add_task(send_email, [user['email']], 'Welcome to RefillGo', 'welcome.html', {
            'login_link': f'{FRONTEND_URL}/login'
        })
    
        response.status_code = 201
        return {
            'message': 'User created successfully.',
            'data': user,
        }
    
    raise validation_error('user', 'Failed to create user.', status=500)


@router.post("/login")
def login(payload: UserLoginSchema, response: Response, db: Session = Depends(get_db)):
    user = authenticate_user(payload, db, response)

    if user:
        response.status_code = 200
        return {
            'message': 'User logged in successfully.',
            'data': user,
        }
    
    raise validation_error('user', 'Failed to login.', status=500)