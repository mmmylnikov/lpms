from notify.models import Provider, Account, Status, Message
from notify.enums import MessageStatuses


def test__provider__str():
    assert str(Provider(name='telegram_bot')) == 'telegram_bot'


def test__account__str():
    assert str(Account(chat_uid='12345678')) == '12345678'


def test__status__str():
    assert str(Status(enabled=True)) == 'True'
    assert str(Status(enabled=False)) == 'False'


def test__message__str():
    assert str(Message(
        text='test ok', status=MessageStatuses.OK.value
    )) == 'test ok: ok'
    assert str(Message(
        text='test error', status=MessageStatuses.ERROR.value
    )) == 'test error: error'
