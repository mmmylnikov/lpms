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
from learn.models import Lesson, Challenge, Track, Homework, HomeworkStatus
from learn.forms import TaskUpdateForm
from learn.meta import StudentLearnMeta, TutorLearnMeta
from learn.enums import HomeworkStatuses
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
        })
        if hasattr(learn_meta, 'week'):
            context.update({
                'week': learn_meta.week,
                })
        return context


class TutorDashboardView(DashboardView):
    template_name = "dashboard/tutor.html"

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        learn_meta = TutorLearnMeta(
            user=self.request.user,
            team=self.team,
            week_number=self.week_number
            ).get_teams()
        context.update({
            'learn_meta': learn_meta,
        })
        return context


class ContentView(LoginRequiredMixin, TemplateView):
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


class TaskViewMixin(LoginRequiredMixin, TemplateView):
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
        if isinstance(self.request.user, AnonymousUser):
            return context
        task, created = Homework.objects.get_or_create(
            user=self.request.user,
            сhallenge=context['challenge'],
            week=context['week'],
            team=self.team,
        )
        if created:
            status = HomeworkStatus(
                student=self.request.user,
                tutor=self.team.tutor,
                homework=task,
                status=HomeworkStatuses.execution.name,
            )
            status.save()
            task.save()
        else:
            if not task:
                status = None
            else:
                status = HomeworkStatus.objects.filter(
                    homework=task, student=self.request.user).last()
        context.update({
            'task': task,
            'status': status,
            'status_sending': 'review',
        })
        return context


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Homework
    form_class = TaskUpdateForm
    template_name = 'dashboard/task_update_form.html'

    def set_obj_status(self, status: str | None) -> Homework:
        obj: Homework = self.get_object()
        if isinstance(self.request.user, AnonymousUser):
            return obj
        if not status:
            return obj
        HomeworkStatus(
            student=self.request.user,
            tutor=obj.team.tutor,
            status=status,
            homework=obj,
        ).save()
        return obj

    def get_success_url(self) -> str:
        return self.request.GET.get('redirect_url', '/')

    def get_context_data(self, **kwargs: reverse_lazy) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        form = context['form']
        status = self.get_object().homeworkstatus_set.last()
        repo_isreadonly = status.status not in [
            HomeworkStatuses.available.name,
            HomeworkStatuses.execution.name,]
        if self.request.method == 'GET' and repo_isreadonly:
            form.fields['repo'].widget.attrs.update({
                'readonly': True,
                'title': 'Вы не можете редактировать '
                         'ссылку после отправки'})
        context.update({
            'status_sending': self.request.GET.get('status_sending'),
            'status': status,
        })
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


class TutorReviewView(TutorDashboardView):
    pass


class PullAutocompleteView(TemplateView):
    template_name = 'dashboard/pull_autocomplete.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if isinstance(self.request.user, AnonymousUser):
            return context
        repo_name = self.request.GET.get('repo')
        if not repo_name:
            repos = Repo.objects.all()
            pulls = Pull.objects.all().select_related('repo')
        else:
            repos = Repo.objects.filter(full_name__icontains=repo_name)
            pulls = Pull.objects.filter(
                html_url__icontains=repo_name).select_related('repo')
        repos_all = Repo.objects.filter(user=self.request.user)
        pulls_all = Pull.objects.filter(repo__user=self.request.user)
        repos_count = repos.count()
        if repos_count > 1:
            context.update({
                'repos': repos,
                'pulls': pulls,
                })
        elif repos_count == 1:
            repo = repos[0]
            pulls = Pull.objects.filter(repo=repo)
            if pulls.count() == 0:
                pulls = repo.update_pulls()
            context.update({
                'pulls': pulls,
                'repos': repos,
            })
        else:
            context.update({
                'repos': repos_all,
                'pulls': pulls_all,
                })
        return context
