from typing import Any

from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.views.generic.detail import DetailView
from markdown import markdown

from course.models import Course


class CourseDetailView(DetailView):
    model = Course

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        context['courses'] = Course.objects.all()
        context['content'] = markdown(self.get_object().description)
        tracks = self.get_object().track_set.all().order_by('created_at')
        context['tracks'] = {
            track: markdown(track.description) for track in tracks}
        return context

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        # return super().get_object(queryset)
        course_id = int(self.request.GET.get('course', 1))
        return Course.objects.get(pk=course_id)
