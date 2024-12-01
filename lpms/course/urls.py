from django.urls import path

from course.views import CourseDetailView, test_handler_error_view
from config import settings

urlpatterns = [
    path('', CourseDetailView.as_view(), name='home'),
    ]

if settings.DEBUG:
    urlpatterns += [
        path('test_handler_status/<int:status_code>', test_handler_error_view)
    ]
