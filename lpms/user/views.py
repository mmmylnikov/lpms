from typing import Any

from django.http.response import HttpResponse as HttpResponse
from django.urls import reverse_lazy
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.shortcuts import redirect

from user.models import User
from user.forms import UserUpdateForm
from learn.meta import LearnMeta
from learn.models import Team
from notify.services import switch_notify, get_notify_status


class UserDetailView(DetailView):
    model = User

    def get_slug_field(self) -> str:
        return "username"

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        context["learn_meta"] = (
            LearnMeta(user=self.get_object())
            .get_teams()
            .get_tasks_learn()
            .check_account_fullness()
        )
        return context

    def render_to_response(
        self, context: dict[str, Any], **response_kwargs: Any
    ) -> HttpResponse:
        redirect_home_response = redirect("home", permanent=False)
        user_request = self.request.user
        if isinstance(user_request, AnonymousUser):
            return redirect_home_response
        user_profile = context['user']
        show_profile_response = super().render_to_response(
            context, **response_kwargs
        )
        if user_request == user_profile:
            return show_profile_response
        else:
            if user_request.is_admin:
                # admin - can watch all users
                return show_profile_response
            elif user_request.is_tutor:
                # tutor - can watch only your students
                teams = Team.objects.filter(tutor=user_request).select_related(
                    "students"
                )
                students_id = set(
                    [ids["students"] for ids in list(teams.values("students"))]
                )
                if user_profile.id in students_id:
                    return show_profile_response
            else:
                # student - can watch only your tutors
                teams = user_request.team_set.all().select_related('tutor')
                tutors_id = set(
                    [ids["tutor"] for ids in list(teams.values("tutor"))]
                )
                if user_profile.id in tutors_id:
                    return show_profile_response
        return redirect_home_response


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm

    def get_success_url(self) -> str:
        return reverse_lazy(
            "user_detail_view", kwargs={"slug": self.request.user.username}
        )

    def get_slug_field(self) -> str:
        return "username"


class UserNotifySwitchView(LoginRequiredMixin, TemplateView):
    template_name = "user/user_notify_switch.html"

    def render_to_response(
        self, context: dict[str, Any], **response_kwargs: Any
    ) -> HttpResponse:
        return redirect("user_detail_view", slug=self.request.user.username)

    def get_context_data(self, **kwargs: reverse_lazy) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if isinstance(self.request.user, AnonymousUser):
            return context
        notify_html = switch_notify(user=self.request.user)
        context.update({"notify_html": notify_html})
        return context


class UserNotifyStatusView(LoginRequiredMixin, TemplateView):
    template_name = "user/user_notify_status.html"

    def get_context_data(self, **kwargs: reverse_lazy) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if isinstance(self.request.user, AnonymousUser):
            return context
        notify_html = get_notify_status(user=self.request.user)
        context.update({"notify_html": notify_html})
        return context
