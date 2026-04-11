from datetime import datetime

from pydantic import EmailStr, model_validator
from shared.models import TrimmedBaseModel
from shared.utils import validation_error


class UserCreateSchema(TrimmedBaseModel):
    first_name: str
    last_name: str
    middle_name: str = None
    email: EmailStr
    phone_number: str = None
    address: str = None 
    password: str = None
    method: str = 'EMAIL'
    role_name: str = 'USER'
    identifier: str = None

    @model_validator(mode="before")
    @classmethod
    def validate_method(cls, values):
        method = values.get('method', '').upper()
        email = values.get('email', '').lower()
        password = values.get('password', '')
        role_name = values.get('role_name', '').upper()

        if method not in ['EMAIL', 'GOOGLE', 'FACEBOOK']:
            return validation_error('method', 'Invalid authentication method. Must be one of: EMAIL, GOOGLE, FACEBOOK.')
        
        if role_name == 'ADMIN':
            return validation_error('role_name', 'Cannot assign ADMIN role.')
        
        if method == 'EMAIL':
            if not email:
                return validation_error('email', 'Email is required for EMAIL method.')
            if not password:
                return validation_error('password', 'Password is required for EMAIL method.')
            
        values['method'] = method
        values['role_name'] = role_name

        if method == 'EMAIL':
            values['identifier'] = email

        return values


class UserLoginSchema(TrimmedBaseModel):
    method: str
    identifier: str
    password: str = None

    @model_validator(mode="before")
    @classmethod
    def validate_method(cls, values):
        method = values.get('method', '').upper()
        identifier = values.get('identifier', '').lower()

        values['method'] = method
        values['identifier'] = identifier

        return values


class UserGenerateResetPasswordTokenSchema(TrimmedBaseModel):
    email: EmailStr


class UserChangePasswordSchema(TrimmedBaseModel):
    token: str
    new_password: str


class PasswordResetToken(TrimmedBaseModel):
    email: EmailStr
    token: str
    expires_at: datetime
