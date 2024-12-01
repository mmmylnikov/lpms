from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from markdown import markdown

from course.models import Course
from learn.meta import LearnMeta


class CourseDetailView(LoginRequiredMixin, TemplateView):
    template_name = "course/course_detail.html"

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "courses": Course.objects.all(),
            }
        )
        course = self.get_object()
        if course:
            tracks = course.track_set.all().order_by("created_at")
            context.update(
                {
                    "course": course,
                    "content": markdown(course.description),
                    "tracks": {
                        track: markdown(track.description) for track in tracks
                    },
                }
            )

        if self.request.user.is_authenticated:
            context["learn_meta"] = (
                LearnMeta(user=self.request.user)
                .get_teams()
                .check_account_fullness()
                .get_support_links(course=course)
            )
        return context

    def get_object(self) -> Course | None:
        course_id_raw = self.request.GET.get("course", "1")
        if not course_id_raw:
            return Course.objects.first()
        return Course.objects.get(pk=int(course_id_raw))


def handler_404_view(
    request: HttpRequest, *args: Any, **kwargs: Any
) -> HttpResponse:
    status = 404
    return render(
        request,
        "error.html",
        {"status_code": status, "status_text": "Страница не найдена"},
        status=status,
    )


def handler_500_view(
    request: HttpRequest, *args: Any, **kwargs: Any
) -> HttpResponse:
    status = 500
    return render(
        request,
        "error.html",
        {"status_code": status, "status_text": "Сервис вернул ошибку"},
        status=status,
    )


def handler_503_view(
    request: HttpRequest, *args: Any, **kwargs: Any
) -> HttpResponse:
    status = 503
    return render(
        request,
        "error.html",
        {
            "status_code": status,
            "status_text": " ".join([
                "Мы проводим техническое обслуживание LMS,",
                "чтобы сделать сервис лучше. Скоро все заработает!"
                ]),
        },
        status=status,
    )


def handler_403_view(
    request: HttpRequest, *args: Any, **kwargs: Any
) -> HttpResponse:
    status = 403
    return render(
        request,
        "error.html",
        {
            "status_code": status,
            "status_text": "Доступ на эту страницу запрещен",
        },
        status=status,
    )


def handler_400_view(
    request: HttpRequest, *args: Any, **kwargs: Any
) -> HttpResponse:
    status = 400
    return render(
        request,
        "error.html",
        {"status_code": status, "status_text": "Неправильный запрос"},
        status=status,
    )


def test_handler_error_view(
    request: HttpRequest, status_code: int
) -> HttpResponse:
    if status_code == 404:
        return handler_404_view(request)
    elif status_code == 500:
        return handler_500_view(request)
    elif status_code == 503:
        return handler_503_view(request)
    elif status_code == 403:
        return handler_403_view(request)
    elif status_code == 400:
        return handler_400_view(request)
    return render(
        request,
        "error.html",
        {"status_code": status_code, "status_text": "Сервис вернул ошибку"},
        status=status_code,
    )
