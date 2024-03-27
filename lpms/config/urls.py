from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('course.urls')),
    path('admin/', admin.site.urls),
    path('users/', include('user.urls')),
    path('dashboard/', include('dashboard.urls')),
    path("__debug__/", include("debug_toolbar.urls")),
]
