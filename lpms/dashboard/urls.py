from django.urls import path
from django.views.generic import TemplateView

from dashboard.views import (StudentDashboardView, TutorDashboardView,
                             ContentView,
                             StudentTaskView, TutorReviewView, TaskUpdateView,
                             PullAutocompleteView,)


urlpatterns = [
     # dashboard: week, tracks (lessons and challenges)
     path('learn/week/<int:week_number>/team/<slug:team_slug>/',
          StudentDashboardView.as_view(), name='student_dashboard_view'),
     path('review/week/<int:week_number>/team/<slug:team_slug>/',
          TutorDashboardView.as_view(), name='tutor_dashboard_view'),
     path('content/<str:section_type>/<int:obj_id>/<str:content_type>/',
          ContentView.as_view(), name='get_dashboard_content'),

     # dashboard: task (execution and review)
     path('learn/week/<int:week_number>/team/<slug:team_slug>/'
          'task/<int:сhallenge_id>/',
          StudentTaskView.as_view(), name='student_task_view'),
     path('review/week/<int:week_number>/team/<slug:team_slug>/'
          'task/<int:сhallenge_id>/user/<str:username>/',
          TutorReviewView.as_view(), name='tutor_review_view'),
     path('task/<int:pk>/update/', TaskUpdateView.as_view(),
          name='task_update_view'),
     path('task/update/success/', TemplateView.as_view(
          template_name='dashboard/task_execution_form_valid.html'),
          name='task_update_success'),

     # form autocomplete
     path('autocomplete/pull/',
          PullAutocompleteView.as_view(),
          name='pull_autocomplete_view'),
    ]
