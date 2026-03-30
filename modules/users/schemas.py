from pydantic import EmailStr
from shared.models import TrimmedBaseModel


class UserCreate(TrimmedBaseModel):
    first_name: str
    last_name: str
    middle_name: str = None
    email: EmailStr
    phone_number: str = None
    address: str = None 