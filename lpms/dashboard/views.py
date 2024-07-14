from enum import Enum
from typing import Any

from django.forms import BaseModelForm
from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound


from course.models import Team
from learn.models import Lesson, Challenge, Track, Homework, HomeworkStatus
from learn.forms import TaskUpdateForm
from learn.meta import StudentLearnMeta, TutorLearnMeta, LearnMeta
from learn.enums import HomeworkStatuses
from user.models import Repo, Pull, User
from user.utils import GithubApi


class DashboardView(LoginRequiredMixin, TemplateView):
    team: Team
    week_number: int

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        team_id = int(str(kwargs["team_slug"]).split("_")[1])
        self.team = Team.objects.select_related("enrollment", "tutor").get(
            id=team_id
        )
        self.week_number = int(str(kwargs["week_number"]))
        context.update(
            {
                "team": self.team,
                "week_number": self.week_number,
            }
        )
        return context


class StudentDashboardView(DashboardView):
    template_name = "dashboard/student.html"

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        learn_meta = (
            StudentLearnMeta(
                user=self.request.user,
                team=self.team,
                week_number=self.week_number,
            )
            .get_teams()
            .get_tasks_learn()
            .add_task_for_week_challenges()
            .get_support_links(
                course=self.team.enrollment.course,
                enrollment=self.team.enrollment,
                team=self.team,
            )
        )
        context.update(
            {
                "learn_meta": learn_meta,
            }
        )
        if hasattr(learn_meta, "week"):
            context.update(
                {
                    "week": learn_meta.week,
                }
            )
        return context

    def get(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse | HttpResponseNotFound:
        context = self.get_context_data(**kwargs)
        if hasattr(context["learn_meta"], "week_current_number"):
            if (
                context["learn_meta"].week_current_number
                < context["week"].number
            ):
                return HttpResponseNotFound()
        return self.render_to_response(context)


class TutorDashboardView(DashboardView):
    template_name = "dashboard/tutor.html"

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        learn_meta = (
            TutorLearnMeta(
                user=self.request.user,
                team=self.team,
                week_number=self.week_number,
            )
            .get_teams()
            .get_support_links(
                course=self.team.enrollment.course,
                enrollment=self.team.enrollment,
                team=self.team,
            )
        )
        context.update(
            {
                "learn_meta": learn_meta,
            }
        )
        return context


class TutorDashboardStatsView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/tutor_stats.html"
    status: HomeworkStatuses = HomeworkStatuses.review

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)

        learn_meta = (
            LearnMeta(user=self.request.user)
            .get_teams()
            .get_tutor_stats(status=self.status)
        )
        context.update({
            "learn_meta": learn_meta,
            "homework_status": self.status})
        return context


class AdminDashboardStatsView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/admin_stats.html"
    status: HomeworkStatuses = HomeworkStatuses.review

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)

        learn_meta = (
            LearnMeta(user=self.request.user)
            .get_teams()
            .get_admin_stats(status=self.status)
        )
        context.update({
            "learn_meta": learn_meta,
            "homework_status": self.status})
        return context


class ContentView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/content.html"

    class SectionMapper(Enum):
        lesson = Lesson
        challenge = Challenge

    class ContentTypeMapper(Enum):
        video = "video"
        slide = "slide"

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        obj_type = self.SectionMapper[str(kwargs["section_type"])].value
        obj = obj_type.objects.get(pk=self.kwargs["obj_id"])
        content_type = self.ContentTypeMapper[
            str(kwargs["content_type"])
        ].value
        content_data = getattr(obj, content_type)

        if content_type == "video":
            context["video_uid"] = obj.video_uid
        elif content_type == "slide":
            context["slide_url"] = obj.slide_embed_url

        context.update(
            {
                "obj": obj,
                "content_type": content_type,
                "content_data": content_data,
            }
        )
        return context


class TaskViewMixin(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/task.html"
    challenge: Challenge
    track: Track

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        challenge_id = str(kwargs["challenge_id"])
        self.challenge = Challenge.objects.get(pk=challenge_id)
        self.track = self.challenge.track
        context.update(
            {
                "challenge": self.challenge,
                "track": self.track,
            }
        )
        return context


class StudentTaskView(TaskViewMixin, StudentDashboardView):
    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        if isinstance(self.request.user, AnonymousUser):
            return context
        task, created = Homework.objects.get_or_create(
            user=self.request.user,
            challenge=context["challenge"],
            week=context["week"],
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
                    homework=task, student=self.request.user
                ).first()
        context.update(
            {
                "task": task,
                "status": status,
                "status_sending": "review",
            }
        )
        return context


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Homework
    form_class = TaskUpdateForm
    template_name = "dashboard/task_update_form.html"

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
        return reverse_lazy("task_update_success")

    def get_context_data(self, **kwargs: reverse_lazy) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        form = context["form"]
        status = self.get_object().homeworkstatus_set.first()
        repo_isreadonly = status.status not in [
            HomeworkStatuses.available.name,
            HomeworkStatuses.execution.name,
        ]
        if self.request.method == "GET" and repo_isreadonly:
            form.fields["repo"].widget.attrs.update(
                {
                    "readonly": True,
                    "title": "Вы не можете редактировать "
                    "ссылку после отправки",
                }
            )
        context.update(
            {
                "status_sending": self.request.GET.get("status_sending"),
                "status_current": self.request.GET.get("status_current"),
                "status": status,
            }
        )
        return context

    def post(
        self, request: HttpRequest, *args: str, **kwargs: reverse_lazy
    ) -> HttpResponse:
        status_sending = self.request.POST.get("status_sending")
        if self.request.POST.get("status_sending") == "available":
            self.set_obj_status(status=status_sending)
            return redirect(self.get_success_url())
        return super().post(request, *args, **kwargs)

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        response = super().form_valid(form)
        status_sending = self.request.POST.get("status_sending")
        status_current = self.request.GET.get("status_current")
        if status_sending != status_current:
            self.set_obj_status(status=status_sending)
        return response


class ReviewViewMixin(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/review.html"
    challenge: Challenge
    track: Track
    student: User

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        challenge_id = str(kwargs["challenge_id"])
        username = str(kwargs["username"])
        self.challenge = Challenge.objects.get(pk=challenge_id)
        self.track = self.challenge.track
        self.student = User.objects.get(username=username)
        context.update(
            {
                "challenge": self.challenge,
                "track": self.track,
                "student": self.student,
            }
        )
        return context


class TutorReviewView(ReviewViewMixin, TutorDashboardView):
    review: Homework | None = None
    status: HomeworkStatus | None = None

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        self.review = Homework.objects.filter(
            user=self.student,
            challenge=self.challenge,
            team=self.team,
            week=context["learn_meta"].week,
        ).first()
        context.update(
            {
                "review": self.review,
            }
        )
        if isinstance(self.request.user, AnonymousUser):
            return context
        self.status = HomeworkStatus.objects.filter(
            student=self.student,
            tutor=self.request.user,
            homework=self.review,
        ).first()
        context.update(
            {
                "status": self.status,
            }
        )
        return context


class TutorReviewCheckView(TemplateView):
    template_name = "dashboard/review_check.html"

    def __add_status(
        self, early_status_instance: HomeworkStatus, status: HomeworkStatuses
    ) -> HomeworkStatus:
        new_status = HomeworkStatus(
            student=early_status_instance.student,
            tutor=early_status_instance.tutor,
            homework=early_status_instance.homework,
            status=status.name,
        )
        new_status.save()
        return new_status

    def __get_github_pr_status(
        self, pr_url: str, tutor_github_login: str
    ) -> HomeworkStatuses:
        pr_reviews = GithubApi().get_pr_by_url(url=pr_url)
        if [
            pr
            for pr in pr_reviews
            if (pr.state == "APPROVED" and pr.user.login == tutor_github_login)
        ]:
            return HomeworkStatuses.approved
        elif [
            pr
            for pr in pr_reviews
            if (
                pr.state == "COMMENTED" and pr.user.login == tutor_github_login
            )
        ]:
            return HomeworkStatuses.correction
        else:
            return HomeworkStatuses.review

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        review = Homework.objects.get(pk=self.kwargs["review_id"])
        status = HomeworkStatus.objects.get(pk=self.kwargs["status_id"])
        if status.status != HomeworkStatuses.review.name:
            context.update({"new_status": None, "reason": "already_review"})
            return context
        if not review.repo:
            context.update({"new_status": None, "reason": "repo_isnotvalid"})
            return context
        github_pr_status = self.__get_github_pr_status(
            pr_url=review.repo,
            tutor_github_login=self.kwargs["tutor_github_login"],
        )
        if github_pr_status == HomeworkStatuses.approved:
            new_status = self.__add_status(status, HomeworkStatuses.approved)
            context.update({"new_status": new_status})
            return context
        elif github_pr_status == HomeworkStatuses.correction:
            new_status = self.__add_status(status, HomeworkStatuses.correction)
            context.update({"new_status": new_status})
            return context
        else:
            context.update({"new_status": None, "reason": "no_data"})
            return context


class PullAutocompleteView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/pull_autocomplete.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if isinstance(self.request.user, AnonymousUser):
            return context
        repo_name = self.request.GET.get("repo")
        if not repo_name:
            repos = Repo.objects.filter(user=self.request.user)
            pulls = Pull.objects.filter(
                repo__user=self.request.user
            ).select_related("repo")
        else:
            repos = Repo.objects.filter(
                user=self.request.user,
                full_name__icontains=repo_name
                )
            pulls = Pull.objects.filter(
                repo__user=self.request.user,
                html_url__icontains=repo_name
            ).select_related("repo")
        repos_count = repos.count()
        if repos_count > 3:
            context.update(
                {
                    "repos": repos,
                    "pulls": pulls,
                }
            )
        elif repos_count >= 1 and repos_count <= 3:
            for repo in repos:
                pulls = Pull.objects.filter(
                    repo__user=self.request.user,
                    repo=repo
                    )
                if pulls.count() == 0:
                    pulls = repo.update_pulls()
            pulls = Pull.objects.filter(
                repo__user=self.request.user,
                repo__in=repos
                )
            context.update(
                {
                    "pulls": pulls,
                    "repos": repos,
                }
            )
        else:
            repos_all = Repo.objects.filter(user=self.request.user)
            if repos_all.count() == 0:
                repos = self.request.user.update_repos()
                context.update(
                    {
                        "repos": repos,
                    }
                )
                return context
            pulls_all = Pull.objects.filter(repo__user=self.request.user)
            context.update(
                {
                    "repos": repos_all,
                    "pulls": pulls_all,
                }
            )
        return context
