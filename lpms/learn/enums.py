from enum import Enum
from dataclasses import dataclass


@dataclass(kw_only=True, slots=True)
class HomeworkStatus:
    name: str
    label: str
    icon: str
    color: str


class HomeworkStatuses(Enum):
    available = HomeworkStatus(name='available',
                               label='Доступно к выполнению',
                               icon='bi bi-square', color='secondary')
    execution = HomeworkStatus(name='execution', label='Выполнение',
                               icon='bi bi-pencil-square', color='danger')
    review = HomeworkStatus(name='review', label='На проверке',
                            icon='bi bi-r-square', color='info')
    correction = HomeworkStatus(name='correction', label='Требует исправлений',
                                icon='bi bi-exclamation-square',
                                color='warning')
    approved = HomeworkStatus(name='approved', label='Принято',
                              icon='bi bi-check-square',
                              color='success')
