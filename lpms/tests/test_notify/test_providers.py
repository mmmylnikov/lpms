from unittest.mock import patch

import pytest

from user.models import User


def test__telegram_bot__has_token(telegram_bot):
    assert telegram_bot.token


def test__telegram_bot__has_api_url(telegram_bot):
    assert telegram_bot.api_url


def test__telegram_bot__has_ssl_context(telegram_bot):
    assert telegram_bot.ssl_context


def test__telegram_bot_get_updates__success(
    telegram_bot, getUpdates_stub_success
):
    with patch.object(
        telegram_bot,
        "get_data_from_request",
        return_value=getUpdates_stub_success,
    ):
        assert len(telegram_bot.get_updates().updates) > 0


def test__telegram_bot_get_updates__empty(
    telegram_bot, getUpdates_stub_empty
):
    with patch.object(
        telegram_bot,
        "get_data_from_request",
        return_value=getUpdates_stub_empty,
    ):
        assert isinstance(telegram_bot.get_updates().updates, list)


def test__telegram_bot_get_updates__error(
        telegram_bot, getUpdates_stub_error
):
    with patch.object(
        telegram_bot,
        "get_data_from_request",
        return_value=getUpdates_stub_error,
    ):
        assert telegram_bot.get_updates().updates is None


def test__telegram_bot__get_last_users_success(
    telegram_bot, getUpdates_stub_success
):
    with patch.object(
        telegram_bot,
        "get_data_from_request",
        return_value=getUpdates_stub_success,
    ):
        telegram_bot.get_updates()
        assert sorted(telegram_bot.get_last_users()) == sorted(
            ["username1", "username2"]
        )

        for update in telegram_bot.updates:
            del update['message']
        assert telegram_bot.get_last_users() == []


def test__telegram_bot__get_last_users_empty(
    telegram_bot, getUpdates_stub_empty
):
    with patch.object(
        telegram_bot,
        "get_data_from_request",
        return_value=getUpdates_stub_empty,
    ):
        telegram_bot.get_updates()
        assert telegram_bot.get_last_users() is None


@pytest.mark.django_db
def test__known_user(
    telegram_bot, getUpdates_stub_success, getUpdates_stub_empty
):
    user = User.objects.create_user(
        username="username", tg_username="UserName1"
    )
    with patch.object(
        telegram_bot,
        "get_data_from_request",
        return_value=getUpdates_stub_success,
    ):
        assert telegram_bot.known_user(user)

        user.tg_username = 'UserName3'
        assert not telegram_bot.known_user(user)

        user.tg_username = None
        user.save()
        assert not telegram_bot.known_user(user)

    with patch.object(
        telegram_bot,
        "get_data_from_request",
        return_value=getUpdates_stub_empty,
    ):
        telegram_bot.get_updates()
        assert not telegram_bot.known_user(user)


@pytest.mark.parametrize('username, chat_id', [
    ('UserName1', '300000001'),
    ('UserName2', '300000002'),
    ('UserName3', None),
    ])
def test__telegram_bot__get_user_chat_id_success(
    username, chat_id, telegram_bot, getUpdates_stub_success
):
    with patch.object(
        telegram_bot,
        "get_data_from_request",
        return_value=getUpdates_stub_success,
    ):
        telegram_bot.get_updates()
        assert telegram_bot.get_user_chat_id(username=username) == chat_id

        for update in telegram_bot.updates:
            del update['message']
        assert telegram_bot.get_user_chat_id(username=username) is None

        telegram_bot.updates = None
        assert telegram_bot.get_user_chat_id(username=username) is None


def test__telegram_bot__send_message_success(
    telegram_bot, sendMessage_stub_success
):
    with patch.object(
        telegram_bot,
        "get_data_from_request",
        return_value=sendMessage_stub_success,
    ):
        assert telegram_bot.send_message(
            chat_id='300000001',
            text='Test message',
        )['result']['text'] == 'Test message'


def test__telegram_bot__send_message_error(
    telegram_bot, sendMessage_stub_error
):
    with patch.object(
        telegram_bot,
        "get_data_from_request",
        return_value=sendMessage_stub_error,
    ):
        assert not telegram_bot.send_message(
            chat_id='300000003',
            text='Test message',
        )['ok']
