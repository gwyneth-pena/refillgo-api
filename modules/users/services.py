

from argon2 import PasswordHasher
from sqlalchemy.orm import Session
from argon2.exceptions import VerifyMismatchError
from modules.users.models import Role, User, UserLogin, UserRole
from modules.users.schemas import UserCreate
from shared.utils import validation_error



def verify_password(hashed_password: str, plain_password: str) -> bool:
    try:
        return PasswordHasher().verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False
    except Exception:
        return False

def add_user(payload: UserCreate, db: Session) -> dict:
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

    return {
        'id': new_user.id,
        'first_name': new_user.first_name,
        'last_name': new_user.last_name,
        'middle_name': new_user.middle_name,
        'email': new_user.email,
        'phone_number': new_user.phone_number,
        'address': new_user.address,
        'roles': [ur.role.name for ur in new_user.user_roles],
        'created_at': new_user.created_at,
        'updated_at': new_user.updated_at,
    }

    
    