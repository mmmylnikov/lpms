from django.template import loader

from config.settings import TELEGRAM_BOT_USERNAME
from user.models import User
from notify.models import Account, Provider, Status, Message
from notify.enums import Providers, MessageTemplates, MessageStatuses
from notify.providers import TelegramBot


def save_message(user: User, account: Account, text: str,
                 status: str, status_comment: str) -> Message:
    message = Message(
        user=user,
        account=account,
        text=text,
        status=status,
        status_comment=status_comment,
    )
    message.save()
    return message


def get_notify_status(user: User) -> str:
    accounts = Account.objects.filter(user=user)
    template = loader.get_template('notify/notify_help.html')
    context = {
        "user": user,
        "accounts": accounts,
        "tg_bot_username": TELEGRAM_BOT_USERNAME,
    }
    return template.render(context)


def switch_notify(user: User) -> bool:
    bot = TelegramBot()
    user_notify_accounts = Account.objects.filter(
        user=user,
        provider=Provider.objects.get(name=Providers.TELEGRAM_BOT.value),
    )
    if user_notify_accounts.count() == 0:
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
    else:
        notify_account = user_notify_accounts.first()
        if not notify_account:
            return False
        account = notify_account
        chat_id = account.chat_uid
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

    message_comment = message_text.name
    if not bot_response['ok']:
        bot_response_comment = bot_response['description']
        message_comment += str(bot_response_comment)

    save_message(
        user=user,
        account=account,
        text=message_text.value,
        status=message_status.value,
        status_comment=message_comment,
    )
    return True


def send_message_homework_status_update(user: User, message: str) -> None:
    if not user.notify or not user.tg_username:
        # print(('Cообщение не отправлено: выключены уведомления'
        #        f'(to: "{user.get_full_name()}", mess:"{message}")'))
        return None

    account = Account.objects.get(user=user)

    bot = TelegramBot()
    bot_response = bot.send_message(account.chat_uid, message)
    if bot_response['ok']:
        message_status = MessageStatuses.OK
    else:
        message_status = MessageStatuses.ERROR

    message_comment = MessageTemplates.TASK_STATUS_UPDATE.name
    if not bot_response['ok']:
        bot_response_comment = bot_response['description']
        message_comment += str(bot_response_comment)
    pass

    save_message(
        user=user,
        account=account,
        text=message,
        status=message_status.value,
        status_comment=message_comment,
    )
