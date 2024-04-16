from enum import Enum


class Providers(Enum):
    TELEGRAM_BOT = 'telegram_bot'


class MessageStatuses(Enum):
    OK = 'ok'
    ERROR = 'error'


class MessageTemplates(Enum):
    NOTIFY_ENABLED = ('*Отлично!* Теперь я буду присылать тебе уведомления '
                      'всякий раз, когда куратор проверит твою работу. '
                      'Или если будет другая важная информация. '
                      'Отключить уведомления всегда можно в профиле.'
                      )
    NOTIFY_DISABLED = ('*Понял!* Больше не буду присылать тебе уведомления')
    TASK_STATUS_UPDATE = ('*Смотри!* Статус твоего задания изменился')
    REVIEW_NEW_STATUS_UPDATE = ('*Смотри!* Тебе прислали работу на проверку')
    REVIEW_STATUS_UPDATE = ('*Ух ты!* Твой студент получил новенькое ревью')
