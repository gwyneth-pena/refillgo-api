from unittest.mock import MagicMock

import pytest

from modules.users.services import authenticate_user


def test_login_success(mocker):

    mock_db = MagicMock()
    mock_response = MagicMock()

    mock_user_login = MagicMock()
    mock_user_login.method = 'EMAIL'
    mock_user_login.identifier = 'john.doe@example.com' 
    mock_user_login.password = 'password'

    mock_db.query.return_value.filter_by.return_value.first.return_value = mock_user_login

    mock_role = MagicMock()
    mock_role.name = 'USER'
    mock_role.id = 1

    mock_user_role = MagicMock()
    mock_user_role.role = mock_role


    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.first_name = 'John'
    mock_user.last_name = 'Doe'
    mock_user.middle_name = ''
    mock_user.email = 'john.doe@example.com'
    mock_user.phone_number = ''
    mock_user.address = ''
    mock_user.created_at = '2023-01-01T00:00:00'
    mock_user.updated_at = '2023-01-01T00:00:00'

    mock_user.user_roles = [mock_user_role]

    mock_db.query.return_value.filter_by.return_value.first.side_effect = [
        mock_user_login, 
        mock_user
    ]

    mocker.patch('modules.users.services.verify_password', return_value=True)
    mocker.patch('modules.users.services.create_access_token', return_value="fake_token")

    res = authenticate_user(mock_user_login, mock_db, mock_response)

    assert res['id'] == 1
    assert res['first_name'] == 'John'
    assert res['last_name'] == 'Doe'
    assert res['middle_name'] == ''
    assert res['email'] == 'john.doe@example.com'
    assert res['phone_number'] == ''
    assert res['address'] == ''
    assert res['roles'] == ['USER']
    assert res['created_at'] == '2023-01-01T00:00:00'
    assert res['updated_at'] == '2023-01-01T00:00:00'
    
    assert mock_response.set_cookie.call_count == 1


def test_login_invalid_credentials_no_user_login_record(mocker):
    mock_db = MagicMock()
    mock_response = MagicMock()

    mock_user_login = MagicMock()
    mock_user_login.method = 'EMAIL'
    mock_user_login.identifier = 'john.doe@example.com' 
    mock_user_login.password = 'password'

    mock_db.query.return_value.filter_by.return_value.first.return_value = None

    with pytest.raises(Exception) as e:
        authenticate_user(mock_user_login, mock_db, mock_response)

    assert e.value.status_code == 422
    assert e.value.detail[0]['msg'] == 'Invalid credentials.'


def test_login_invalid_credentials_wrong_password(mocker):
    mock_db = MagicMock()
    mock_response = MagicMock()

    mock_user_login = MagicMock()
    mock_user_login.method = 'EMAIL'
    mock_user_login.identifier = 'john.doe@example.com'
    mock_user_login.password = 'password'

    mock_db.query.return_value.filter_by.return_value.first.return_value = mock_user_login

    mocker.patch('modules.users.services.verify_password', return_value=False)

    with pytest.raises(Exception) as e:
        authenticate_user(mock_user_login, mock_db, mock_response)

    assert e.value.status_code == 422
    assert e.value.detail[0]['msg'] == 'Invalid credentials.'