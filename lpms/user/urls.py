from django.urls import path, include

from user.views import (UserDetailView, UserUpdateView,
                        UserNotifyStatusView, UserNotifySwitchView)


urlpatterns = [
    path('accounts/', include('allauth.urls')),
    path('profile/<str:slug>/', UserDetailView.as_view(),
         name='user_detail_view'),
    path('profile/<str:slug>/edit/', UserUpdateView.as_view(),
         name='user_update_view'),
    path('profile/<str:slug>/notify_switch/', UserNotifySwitchView.as_view(),
         name='user_notify_switch_view'),
    path('profile/<str:slug>/notify_status/', UserNotifyStatusView.as_view(),
         name='user_notify_status_view'),
    ]
