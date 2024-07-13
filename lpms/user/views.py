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
        # return super().render_to_response(context, **response_kwargs)

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
