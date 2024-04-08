from django.template import loader

from user.models import User
from notify.models import Account, Provider, Status, Message
from notify.enums import Providers, MessageTemplates, MessageStatuses
from notify.providers import TelegramBot


def get_notify_status(user: User) -> str:
    accounts = Account.objects.filter(user=user)
    template = loader.get_template('notify/notify_help.html')
    context = {'user': user, 'accounts': accounts}
    return template.render(context)


def switch_notify(user: User) -> bool:
    bot = TelegramBot()
    known_user = bot.known_user(user)
    if not known_user:
        return False
    if not user.tg_username:
        return False
    chat_id = bot.get_user_chat_id(username=user.tg_username)
    if not chat_id:
        return False
    account, created = Account.objects.get_or_create(
        user=user,
        provider=Provider.objects.get(name=Providers.TELEGRAM_BOT.value),
        chat_uid=chat_id,
    )
    status = Status(
        user=user,
        account=account,
        enabled=user.switch_notify(),
    )
    status.save()
    if user.notify:
        message_text = MessageTemplates.NOTIFY_ENABLED
    else:
        message_text = MessageTemplates.NOTIFY_DISABLED

    bot_response = bot.send_message(chat_id, message_text.value)
    if bot_response['ok']:
        message_status = MessageStatuses.OK
    else:
        message_status = MessageStatuses.ERROR

    message = Message(
        user=user,
        account=account,
        text=message_text.value,
        status=message_status.value,
        status_comment=message_text.name,
    )
    if not bot_response['ok']:
        bot_response_comment = bot_response['description']
        if not message.status_comment:
            message.status_comment = bot_response_comment
        else:
            message.status_comment += f"; {bot_response_comment}"
    message.save()
    return True
