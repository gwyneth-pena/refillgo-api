import datetime
from unittest.mock import MagicMock

import pytest

from modules.users.schemas import UserChangePasswordSchema
from modules.users.services import change_password, get_reset_password_token


async def test_get_reset_password_token_success(mocker):
    mock_db = MagicMock()
    mock_mongo_db = mocker.AsyncMock()

    mock_login = MagicMock()
    mock_login.method = 'EMAIL'
    mock_login.identifier = 'john.doe@example.com'

    mock_db.query.return_value.filter_by.return_value.first.return_value = mock_login


    mock_mongo_db.passwordtokens.insert_one.return_value = None
    mock_mongo_db.passwordtokens.create_index.return_value = None

    res = await get_reset_password_token('john.doe@example.com', mock_db, mock_mongo_db)

    assert isinstance(res, str)
    assert len(res) > 0


async def test_get_reset_password_token_invalid_email(mocker):
    mock_db = MagicMock()
    mock_mongo_db = mocker.AsyncMock()

    mock_login = MagicMock()
    mock_login.method = 'EMAIL'
    mock_login.identifier = 'john.doe@example.com'

    mock_db.query.return_value.filter_by.return_value.first.return_value = None
    
    with pytest.raises(Exception) as e:
        await get_reset_password_token('john.doe@example.com', mock_db, mock_mongo_db)

    assert e.value.status_code == 422
    assert e.value.detail[0]['msg'] == 'Email does not exist.'


async def test_change_password_success(mocker):
    mock_db = MagicMock()
    mock_mongo_db = mocker.AsyncMock()

    mock_login = MagicMock()
    mock_login.method = 'EMAIL'
    mock_login.identifier = 'john.doe@example.com'
    mock_login.password = 'password'

    mock_db.query.return_value.filter_by.return_value.first.return_value = mock_login
    
    mock_mongo_db.passwordtokens.find_one.return_value = {
        'token': 'token',
        'expires_at': datetime.datetime.now() + datetime.timedelta(minutes=15),
        'email': 'john.doe@example.com',
    }

    mocker.patch('modules.users.services.get_hashed_password', return_value='hashed_password')

    res = await change_password(UserChangePasswordSchema(token='token', new_password='new_password'), mock_db, mock_mongo_db)

    assert res == True


async def test_change_password_invalid_token(mocker):
    mock_db = MagicMock()
    mock_mongo_db = mocker.AsyncMock()

    mock_login = MagicMock()
    mock_login.method = 'EMAIL'
    mock_login.identifier = 'john.doe@example.com'
    mock_login.password = 'password'

    mock_db.query.return_value.filter_by.return_value.first.return_value = mock_login
    
    mock_mongo_db.passwordtokens.find_one.return_value = None

    with pytest.raises(Exception) as e:
        await change_password(UserChangePasswordSchema(token='token', new_password='new_password'), mock_db, mock_mongo_db)

    assert e.value.status_code == 422
    assert e.value.detail[0]['msg'] == 'Invalid token.'


async def test_change_password_expired_token(mocker):
    mock_db = MagicMock()
    mock_mongo_db = mocker.AsyncMock()

    mock_login = MagicMock()
    mock_login.method = 'EMAIL'
    mock_login.identifier = 'john.doe@example.com'
    mock_login.password = 'password'

    mock_db.query.return_value.filter_by.return_value.first.return_value = mock_login
    
    mock_mongo_db.passwordtokens.find_one.return_value = {
        'token': 'token',
        'expires_at': datetime.datetime.now() - datetime.timedelta(minutes=15),
        'email': 'john.doe@example.com',
    }

    with pytest.raises(Exception) as e:
        await change_password(UserChangePasswordSchema(token='token', new_password='new_password'), mock_db, mock_mongo_db)

    assert e.value.status_code == 422
    assert e.value.detail[0]['msg'] == 'Token has expired.'