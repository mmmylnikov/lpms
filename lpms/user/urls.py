from django.urls import path, include

from user.views import UserDetailView, UserUpdateView


urlpatterns = [
    path('accounts/', include('allauth.urls')),
    path('profile/<str:slug>/', UserDetailView.as_view(),
         name='user_detail_view'),
    path('profile/<str:slug>/edit/', UserUpdateView.as_view(),
         name='user_update_view'),
    ]
