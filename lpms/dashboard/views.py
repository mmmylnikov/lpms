from enum import Enum
from typing import Any

from django.forms import BaseModelForm
from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.http import HttpRequest, HttpResponse

from course.models import Team
from learn.models import Lesson, Challenge, Track, Homework
from learn.forms import TaskUpdateForm
from learn.meta import StudentLearnMeta
from user.models import Repo, Pull


class DashboardView(LoginRequiredMixin, TemplateView):
    team: Team
    week_number: int

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        team_id = int(str(kwargs['team_slug']).split('_')[1])
        self.team = Team.objects.select_related(
            'enrollment', 'tutor').get(id=team_id)
        self.week_number = int(str(kwargs['week_number']))
        context.update({
            'team': self.team,
            'week_number': self.week_number,
        })
        return context


class StudentDashboardView(DashboardView):
    template_name = "dashboard/student.html"

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        learn_meta = StudentLearnMeta(
            user=self.request.user,
            team=self.team,
            week_number=self.week_number
            ).get_teams(
            ).get_tasks_learn(
            ).add_task_for_week_challenges()
        context.update({
            'learn_meta': learn_meta,
            'week': learn_meta.week,
        })
        return context


class TutorDashboardView(DashboardView):
    template_name = "dashboard/tutor.html"


class ContentView(TemplateView):
    template_name = "dashboard/content.html"

    class SectionMapper(Enum):
        lesson = Lesson
        challenge = Challenge

    class ContentTypeMapper(Enum):
        video = 'video'

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        obj_type = self.SectionMapper[str(kwargs['section_type'])].value
        obj = obj_type.objects.get(pk=self.kwargs['obj_id'])
        content_type = self.ContentTypeMapper[
            str(kwargs['content_type'])].value
        content_data = getattr(obj, content_type)

        if content_type == 'video':
            context['video_uid'] = obj.video_uid

        context.update({
            'obj': obj,
            'content_type': content_type,
            'content_data': content_data,
        })
        return context


class TaskViewMixin(TemplateView):
    template_name = "dashboard/task.html"
    challenge: Challenge
    track: Track

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        challenge_id = str(kwargs['сhallenge_id'])
        self.challenge = Challenge.objects.get(pk=challenge_id)
        self.track = self.challenge.track
        context.update({
            'challenge': self.challenge,
            'track': self.track,
        })
        return context


class StudentTaskView(TaskViewMixin, StudentDashboardView):
    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        task, created = Homework.objects.get_or_create(
            user=self.request.user,
            сhallenge=context['challenge'],
            week=context['week'],
            team=self.team,
        )
        if created:
            task.status = 'execution'
            task.save()
        context.update({
            'task': task,
            'status_sending': 'review',
        })
        return context


class TaskUpdateView(UpdateView):
    model = Homework
    form_class = TaskUpdateForm
    template_name = 'dashboard/task_update_form.html'

    def set_obj_status(self, status: str | None) -> Homework:
        obj = self.get_object()
        obj.status = status
        obj.save()
        return obj

    def get_success_url(self) -> str:
        return self.request.GET.get('redirect_url', '/')

    def get_context_data(self, **kwargs: reverse_lazy) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['status_sending'] = self.request.GET.get('status_sending')
        return context

    def post(self,
             request: HttpRequest, *args: str,
             **kwargs: reverse_lazy) -> HttpResponse:
        status_sending = self.request.POST.get('status_sending')
        if self.request.POST.get('status_sending') == 'available':
            self.set_obj_status(status=status_sending)
            return redirect(self.get_success_url())
        return super().post(request, *args, **kwargs)

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        response = super().form_valid(form)
        status_sending = self.request.POST.get('status_sending', )
        self.set_obj_status(status=status_sending)
        return response


class TutorTaskView(TaskViewMixin, TutorDashboardView):
    pass


class PullAutocompleteView(TemplateView):
    template_name = 'dashboard/pull_autocomplete.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if isinstance(self.request.user, AnonymousUser):
            return context
        repo_name = self.request.GET.get('repo')
        if not repo_name:
            return context
        repos = Repo.objects.filter(full_name__icontains=repo_name)
        repos_all = Repo.objects.filter(user=self.request.user)
        repos_count = repos.count()
        if repos_count > 1:
            context.update({'repos': repos})
        elif repos_count == 1:
            repo = repos[0]
            pulls = Pull.objects.filter(repo=repo)
            if pulls.count() == 0:
                pulls = repo.update_pulls()
            context.update({
                'pulls': pulls
            })
        else:
            context.update({'repos': repos_all})
        return context
