import pytest
import json

from notify.providers import TelegramBot


@pytest.fixture
def telegram_bot():
    return TelegramBot(token='token')


@pytest.fixture
def getUpdates_stub_error() -> dict[str, str]:
    return json.loads(
        '{"ok":false,"error_code":401,"description":"Unauthorized"}'
    )


@pytest.fixture
def getUpdates_stub_empty() -> dict[str, str]:
    return json.loads('{"ok":true,"result":[]}')


@pytest.fixture
def getUpdates_stub_success() -> dict[str, str]:
    return json.loads('''
        {
        "ok": true,
        "result": [
            {
                "update_id": 100000001,
                "message": {
                    "message_id": 200000001,
                    "from": {
                        "id": 300000001,
                        "is_bot": false,
                        "first_name": "FirstName1",
                        "last_name": "LastName1",
                        "username": "UserName1",
                        "language_code": "ru"
                        },
                    "chat": {
                        "id": 300000001,
                        "first_name": "FirstName1",
                        "last_name": "LastName1",
                        "username": "UserName1",
                        "type": "private"
                        },
                "date": 1730000000,
                "text": "Text1"
                }
            },
            {
                "update_id": 100000002,
                "message": {
                    "message_id": 200000002,
                    "from": {
                        "id": 300000002,
                        "is_bot": false,
                        "first_name": "FirstName2",
                        "last_name": "LastName2",
                        "username": "UserName2",
                        "language_code": "ru"
                        },
                    "chat": {
                        "id": 300000002,
                        "first_name": "FirstName2",
                        "last_name": "LastName2",
                        "username": "UserName2",
                        "type": "private"
                        },
                "date": 1740000000,
                "text": "Text2"
                }
            }
            ]
        }
''')


@pytest.fixture
def sendMessage_stub_success() -> dict[str, str]:
    return json.loads('''
        {
        "ok": true,
        "result": {
            "message_id": 200000003,
            "from": {
                "id": 9000000001,
                "is_bot": true,
                "first_name": "BotFirstName",
                "username": "BotUserName"
                },
            "chat": {
                "id": 300000001,
                "first_name": "FirstName1",
                "last_name": "LastName1",
                "username": "UserName1",
                "type": "private"
                },
            "date": 1750000000,
            "text": "Test message"
            }
        }
''')


@pytest.fixture
def sendMessage_stub_error() -> dict[str, str]:
    return json.loads('''
        {
        "ok": false,
        "error_code": 400,
        "description": "Bad Request: chat not found"
        }
''')
