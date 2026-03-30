

from sqlalchemy.orm import Session

from modules.users.schemas import UserCreate


def create_user(payload: UserCreate, db: Session) -> dict:
    pass
    