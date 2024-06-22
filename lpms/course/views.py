from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from markdown import markdown

from course.models import Course
from learn.meta import LearnMeta


class CourseDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'course/course_detail.html'

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        context.update({
            'courses': Course.objects.all(),
        })
        course = self.get_object()
        if course:
            tracks = course.track_set.all().order_by('created_at')
            context.update({
                'course': course,
                'content': markdown(course.description),
                'tracks': {
                    track: markdown(track.description) for track in tracks},
            })

        if self.request.user.is_authenticated:
            context['learn_meta'] = LearnMeta(
                user=self.request.user).get_teams()
        return context

    def get_object(self) -> Course | None:
        course_id_raw = self.request.GET.get('course', '1')
        if not course_id_raw:
            return Course.objects.first()
        return Course.objects.get(pk=int(course_id_raw))
