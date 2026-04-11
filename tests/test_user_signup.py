from unittest.mock import MagicMock

from httpcore import Response
import pytest
from modules.users.schemas import UserCreateSchema
from modules.users.services import add_user

async def test_add_user_success(mocker):
    mock_db = MagicMock()
    
    user_data = UserCreateSchema(
        first_name='John',
        last_name='Doe',
        email='john.doe@example.com',
        password='password',
        method='EMAIL',
        role_name='USER',
        identifier='john.doe@example.com',
    )

    mock_response = MagicMock(spec=Response)

    mock_auth_func = mocker.patch('modules.users.services.authenticate_user', new_callable=mocker.AsyncMock)
    mock_auth_func.return_value = {
        'id': 1,
        'first_name': 'John',
        'last_name': 'Doe',
        'middle_name': '',
        'email': 'john.doe@example.com',
        'phone_number': '',
        'address': '',
        'roles': ['USER'],
        'created_at': '2023-01-01T00:00:00',
        'updated_at': '2023-01-01T00:00:00',
    }

    mock_db.query.return_value.filter_by.return_value.first.side_effect = [
        None,           # existing_user check -> None (Success)
        MagicMock(),    # existing_role check -> Found (Success)
        None            # existing_identifier check -> None (Success)
    ]
    
    res = await add_user(user_data, mock_db, mock_response)


    assert res['email'] == 'john.doe@example.com'
    mock_auth_func.assert_called_once()


async def test_add_user_existing_user(mocker):
    mock_db = MagicMock()
    
    user_data = UserCreateSchema(
        first_name='John',
        last_name='Doe',
        email='john.doe@example.com',
        password='password',
        method='EMAIL',
        role_name='USER',
        identifier='john.doe@example.com',
    )

    mock_response = MagicMock(spec=Response)

    mock_auth_func = mocker.patch('modules.users.services.authenticate_user', new_callable=mocker.AsyncMock)
    mock_auth_func.return_value = {
        'id': 1,
        'first_name': 'John',
        'last_name': 'Doe',
        'middle_name': '',
        'email': 'john.doe@example.com',
        'phone_number': '',
        'address': '',
        'roles': ['USER'],
        'created_at': '2023-01-01T00:00:00',
        'updated_at': '2023-01-01T00:00:00',
    }

    mock_db.query.return_value.filter_by.return_value.first.return_value = {
        'id': 1,
        'first_name': 'John',
        'last_name': 'Doe',
        'middle_name': '',
        'email': 'john.doe@example.com',
        'phone_number': '',
        'address': '',
        'roles': ['USER'],
        'created_at': '2023-01-01T00:00:00',
        'updated_at': '2023-01-01T00:00:00',
    }

    with pytest.raises(Exception) as e:
        await add_user(user_data, mock_db, mock_response)

    assert e.value.status_code == 422
    assert e.value.detail[0]['loc'] == ['body', 'email']
    assert e.value.detail[0]['msg'] == 'Email already exists.'
    mock_auth_func.assert_not_called()

 

