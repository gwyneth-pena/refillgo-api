from fastapi import APIRouter

from v1.endpoints import users

v1_router = APIRouter()

v1_router.include_router(users.router, prefix="/users", tags=["Users"])

