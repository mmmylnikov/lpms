from pytest import mark
from notify.enums import MessageStatuses, MessageTemplates, Providers


@mark.parametrize("key", ['OK', 'ERROR'])
def test__message_statuses__enum_has_key(key):
    assert key in list(MessageStatuses.__members__.keys())


@mark.parametrize(
    "key",
    [
        "NOTIFY_ENABLED",
        "NOTIFY_DISABLED",
        "TASK_STATUS_UPDATE",
        "REVIEW_NEW_STATUS_UPDATE",
        "REVIEW_STATUS_UPDATE",
    ],
)
def test__message_templates__enum_has_key(key):
    assert key in list(MessageTemplates.__members__.keys())


@mark.parametrize("key", ['TELEGRAM_BOT'])
def test__providers__enum_has_key(key):
    assert key in list(Providers.__members__.keys())
