from enum import Enum
from dataclasses import dataclass


@dataclass(kw_only=True, slots=True)
class HomeworkStatus:
    name: str
    label: str
    label_plural: str
    label_action_student: str
    label_action_tutor: str
    icon: str
    color: str


class HomeworkStatuses(Enum):
    available = HomeworkStatus(
        name="available",
        label="Доступно к выполнению",
        label_plural="Доступные к выполнению",
        label_action_student="Открыто",
        label_action_tutor="Открыто",
        icon="bi bi-square",
        color="secondary",
    )
    execution = HomeworkStatus(
        name="execution",
        label="Выполнение",
        label_plural="Выполняются",
        label_action_student="Открыто",
        label_action_tutor="Открыто",
        icon="bi bi-pencil-square",
        color="danger",
    )
    review = HomeworkStatus(
        name="review",
        label="На проверке",
        label_plural="На проверке",
        label_action_student="Проверено",
        label_action_tutor="Отправлено",
        icon="bi bi-r-square",
        color="info",
    )
    correction = HomeworkStatus(
        name="correction",
        label="Требует исправлений",
        label_plural="Требуют исправлений",
        label_action_student="Получено",
        label_action_tutor="Проверено",
        icon="bi bi-exclamation-square",
        color="warning",
    )
    approved = HomeworkStatus(
        name="approved",
        label="Принято",
        label_plural="Приняты",
        label_action_student="Получено",
        label_action_tutor="Отправлено",
        icon="bi bi-check-square",
        color="success",
    )
