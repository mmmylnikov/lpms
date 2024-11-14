from django.urls import path
from django.views.generic import TemplateView

from dashboard.views import (StudentDashboardView, StudentTaskView,
                             TutorDashboardView, TutorReviewView,
                             ContentView, PullAutocompleteView,
                             TaskUpdateView, ReviewUpdateView,
                             TutorReviewCheckView,
                             TutorDashboardStatsView,
                             AdminDashboardStatsView,
                             )
from learn.enums import HomeworkStatuses


urlpatterns = [
     # dashboard: week, tracks (lessons and challenges)
     path('learn/week/<int:week_number>/team/<slug:team_slug>/',
          StudentDashboardView.as_view(), name='student_dashboard_view'),
     path('review/week/<int:week_number>/team/<slug:team_slug>/',
          TutorDashboardView.as_view(), name='tutor_dashboard_view'),
     path('content/<str:section_type>/<int:obj_id>/<str:content_type>/',
          ContentView.as_view(), name='get_dashboard_content'),

     # dashboard: analytics for tutor
     path('review/stats/review/',
          TutorDashboardStatsView.as_view(status=HomeworkStatuses.review),
          name='tutor_dashboard_stats_review_view'),
     path('review/stats/correction/',
          TutorDashboardStatsView.as_view(status=HomeworkStatuses.correction),
          name='tutor_dashboard_stats_correction_view'),
     path('review/stats/execution/',
          TutorDashboardStatsView.as_view(status=HomeworkStatuses.execution),
          name='tutor_dashboard_stats_execution_view'),

     # dashboard: analytics for admin
     path('review/admin_stats/review/',
          AdminDashboardStatsView.as_view(status=HomeworkStatuses.review),
          name='admin_dashboard_stats_review_view'),
     path('review/admin_stats/correction/',
          AdminDashboardStatsView.as_view(status=HomeworkStatuses.correction),
          name='admin_dashboard_stats_correction_view'),
     path('review/admin_stats/execution/',
          AdminDashboardStatsView.as_view(status=HomeworkStatuses.execution),
          name='admin_dashboard_stats_execution_view'),

     # dashboard: task (execution and review)
     path('learn/week/<int:week_number>/team/<slug:team_slug>/'
          'task/<int:challenge_id>/',
          StudentTaskView.as_view(), name='student_task_view'),
     path('review/week/<int:week_number>/team/<slug:team_slug>/'
          'task/<int:challenge_id>/user/<str:username>/',
          TutorReviewView.as_view(), name='tutor_review_view'),
     path('task/<int:pk>/update/', TaskUpdateView.as_view(),
          name='task_update_view'),
     path('review/<int:pk>/update/', ReviewUpdateView.as_view(),
          name='review_update_view'),
     path('task/update/success/', TemplateView.as_view(
          template_name='dashboard/task_execution_form_valid.html'),
          name='task_update_success'),
     path('review/check/<int:review_id>/<int:status_id>/<str:tutor_github_login>/',  # noqa
          TutorReviewCheckView.as_view(),
          name='review_check_view'),
     # form autocomplete
     path('autocomplete/pull/',
          PullAutocompleteView.as_view(),
          name='pull_autocomplete_view'),
    ]
