from enum import Enum

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from course.models import Team
from learn.models import Lesson, Challenge
from learn.meta import StudentLearnMeta


class DashboardView(LoginRequiredMixin, TemplateView):
    team: Team
    week_number: int

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        team_id = int(str(kwargs['team_slug']).split('_')[1])
        self.team = Team.objects.get(id=team_id)
        self.week_number = int(str(kwargs['week_number']))
        return context


class StudentDashboardView(DashboardView):
    template_name = "dashboard/student.html"

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        learn_meta = StudentLearnMeta(
            user=self.request.user,
            team=self.team,
            week_number=self.week_number).get_teams()
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
