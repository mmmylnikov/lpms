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
    if kwargs.get('raw'):
        # don't call if loaddata from fixtures
        return
    status = instance.status
    # Student notify
    if status != HomeworkStatuses.available.name:
        message = MessageTemplates.TASK_STATUS_UPDATE.value
        status_text = HomeworkStatuses[status].value.label

        message += f' на "{status_text}".\n'
        message += f'Задание: `{instance.homework.challenge.name}`'
        if instance.homework.tutor_comment:
            message += '\nКомментарий куратора: '
            message += f'`{instance.homework.tutor_comment}`'
        send_message_homework_status_update(user=instance.student,
                                            message=message)
    # Tutor notify
    if status == HomeworkStatuses.review.name:
        message = MessageTemplates.REVIEW_NEW_STATUS_UPDATE.value
        message += f'\nот: "`{instance.student.get_full_name()}`".\n'
        message += f'задание: `{instance.homework.challenge.name}`'
        send_message_homework_status_update(user=instance.tutor,
                                            message=message)
    if status in [HomeworkStatuses.correction.name,
                  HomeworkStatuses.approved.name]:
        message = MessageTemplates.REVIEW_STATUS_UPDATE.value
        message += f'\nстудент: "`{instance.student.get_full_name()}`".\n'
        message += f'задание: `{instance.homework.challenge.name}`'
