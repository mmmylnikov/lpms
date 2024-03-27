from django.urls import path

from dashboard.views import (StudentDashboardView, TutorDashboardView,
                             ContentView)


urlpatterns = [
     path('learn/week/<int:week_number>/team/<slug:team_slug>/',
          StudentDashboardView.as_view(),
          name='student_dashboard_view'),
     path('review/week/<int:week_number>/team/<slug:team_slug>/',
          TutorDashboardView.as_view(),
          name='tutor_dashboard_view'),
     path('content/<str:section_type>/<int:obj_id>/<str:content_type>/',
          ContentView.as_view(),
          name='get_dashboard_content'),
    ]
