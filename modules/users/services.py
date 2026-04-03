import datetime
from argon2 import PasswordHasher
from httpcore import Response
import jwt
from sqlalchemy.orm import Session
from argon2.exceptions import VerifyMismatchError
from config import SECRET_KEY
from modules.users.models import Role, User, UserLogin, UserRole
from modules.users.schemas import UserCreateSchema, UserLoginSchema
from shared.utils import validation_error



def verify_password(hashed_password: str, plain_password: str) -> bool:
    try:
        return PasswordHasher().verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False
    except Exception:
        return False
    

def create_access_token(data: dict, expiry_seconds: int = 3600) -> str:
    to_encode = data.copy()

    expire = datetime.datetime.now() + datetime.timedelta(seconds=expiry_seconds)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

    return encoded_jwt


def add_user(payload: UserCreateSchema, db: Session, response: Response) -> dict:
    existing_user = db.query(User).filter_by(email=payload.email).first()

    if existing_user:
        raise validation_error('email', 'Email already exists.')

    existing_role = db.query(Role).filter_by(name=payload.role_name).first()

    if not existing_role:
        raise validation_error('role_name', 'Role does not exist.')
    
    existing_identifier = db.query(UserLogin).filter_by(identifier=payload.identifier).first()

    if existing_identifier:
        raise validation_error('identifier', 'Identifier already exists.')

    new_user = User(
        first_name=payload.first_name,
        last_name=payload.last_name,
        middle_name=payload.middle_name,
        email=payload.email,
        phone_number=payload.phone_number,
        address=payload.address,
    )

    user_role = UserRole(role_id=existing_role.id)
    new_user.user_roles.append(user_role)

    hashed_password = PasswordHasher(
        memory_cost=65536, # 64MB of RAM
        time_cost=3,       # 3 iterations
        parallelism=4
    ).hash(payload.password)

    new_user.logins.append(
        UserLogin(
            method=payload.method,
            identifier=payload.identifier,
            password=hashed_password,
        )
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return authenticate_user(UserLogin(method=payload.method, identifier=payload.identifier, password=payload.password), db, response=response)

    
def authenticate_user(payload: UserLoginSchema, db: Session, response: Response) -> dict:
    user_login = db.query(UserLogin).filter_by(method=payload.method, identifier=payload.identifier).first()

    if not user_login or not verify_password(user_login.password, payload.password):
        raise validation_error('email', 'Invalid credentials.')

    user = db.query(User).filter_by(id=user_login.user_id).first()

    access_token = create_access_token({
        'user_id': user.id,
        'roles': [ur.role.name for ur in user.user_roles],
    }, expiry_seconds=7200)

    response.set_cookie(
        key="access_token", 
        value=access_token, 
        httponly=True,   
        max_age=7200,     
        expires=7200,  
        samesite="lax",    
        secure=False      
    )

    return {
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'middle_name': user.middle_name,
        'email': user.email,
        'phone_number': user.phone_number,
        'address': user.address,
        'roles': [ur.role.name for ur in user.user_roles],
        'created_at': user.created_at,
        'updated_at': user.updated_at,
    }
