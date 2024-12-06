from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from config import settings


class SuperuserDebugMiddleware:
    def __init__(self, get_response: Any) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if not settings.SITE_REPAIR:
            return self.get_response(request)
        if not request.user.is_authenticated:
            return self.handle_user_debug(request)
        elif request.user.is_superuser:
            return self.handle_superuser_debug(request)
        else:
            return self.handle_user_debug(request)

    def handle_user_debug(self, request: HttpRequest) -> HttpResponse:
        context = {
            "status_code": 503,
            "status_text": " ".join([
                "Мы проводим техническое обслуживание LMS,",
                "чтобы сделать сервис лучше. Скоро все заработает!"
            ]),
        }
        return render(request, 'error.html', context)

    def handle_superuser_debug(self, request: HttpRequest) -> HttpResponse:
        return self.get_response(request)
