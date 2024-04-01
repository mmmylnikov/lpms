from django.urls import path

from course.views import CourseDetailView

urlpatterns = [
    path('', CourseDetailView.as_view(), name='home'),
    ]
