from config import FRONTEND_URL
from fastapi import APIRouter, Response
from fastapi.params import Depends
from shared.email import send_email
from sqlalchemy.orm import Session
from pymongo import AsyncMongoClient
from db import get_db, get_mongo_db
from modules.users.schemas import UserCreateSchema, UserGenerateResetPasswordTokenSchema, UserLoginSchema
from modules.users.services import add_user, authenticate_user, get_reset_password_token
from shared.utils import validation_error
from fastapi import BackgroundTasks


router = APIRouter()

@router.post("/")
def create_user(payload: UserCreateSchema, response: Response,  background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user = add_user(payload, db, response)

    if not user:
        raise validation_error('user', 'Failed to create user.', status=500)

    background_tasks.add_task(send_email, [user['email']], 'Welcome to RefillGo', 'welcome.html', {
        'login_link': f'{FRONTEND_URL}/login'
    })
    
    response.status_code = 201
    return {
        'message': 'User created successfully.',
        'data': user,
    }
    

@router.post("/login")
def login(payload: UserLoginSchema, response: Response, db: Session = Depends(get_db)):
    user = authenticate_user(payload, db, response)

    if not user:
        raise validation_error('user', 'Failed to login.', status=500)

    response.status_code = 200
    return {
        'message': 'User logged in successfully.',
        'data': user,
    }
    

@router.post("/generate-reset-password-token")
async def generate_reset_password_token(payload: UserGenerateResetPasswordTokenSchema, response: Response, background_tasks: BackgroundTasks, db: Session = Depends(get_db), mongo_db: AsyncMongoClient = Depends(get_mongo_db)):
    token = await get_reset_password_token(payload.email, db, mongo_db)

    if not token:
        raise validation_error('email', 'Failed to generate reset password token.')

    background_tasks.add_task(send_email, [payload.email], 'Password Reset', 'password_reset.html', {
        'reset_link': f"{FRONTEND_URL}/reset-password?token={token}",
        'expiry': '15 minutes',
    })
    
    response.status_code = 201
    return {
        'message': 'Password reset link has been sent to your email.',
    }