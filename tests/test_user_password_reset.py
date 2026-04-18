import datetime
from unittest.mock import MagicMock

from modules.users.services import get_reset_password_token


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