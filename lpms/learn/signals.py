from typing import Any

from django.db.models.signals import post_save
from django.dispatch import receiver

from learn.models import HomeworkStatus
from learn.enums import HomeworkStatuses
from notify.services import (
    send_message_homework_status_update,
)
from notify.enums import MessageTemplates


@receiver(post_save, sender=HomeworkStatus)
def send_message_handler(
        instance: HomeworkStatus,
        *args: tuple, **kwargs: dict[str, Any]) -> None:
    status = instance.status
    if status != HomeworkStatuses.available.name:
        message = MessageTemplates.TASK_STATUS_UPDATE.value
        status_text = HomeworkStatuses[status].value.label

        message += f' на "{status_text}".\n'
        message += f'Задание: `{instance.homework.сhallenge.name}`'
        send_message_homework_status_update(user=instance.student,
                                            message=message)
