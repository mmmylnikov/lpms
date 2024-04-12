from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('course.urls')),
    path('admin/', admin.site.urls),
    path('users/', include('user.urls')),
    path('dashboard/', include('dashboard.urls')),
    path("__debug__/", include("debug_toolbar.urls")),
]

admin.site.site_header = "Панель администрирования LPMS"
admin.site.index_title = "LPMS | Администрирование портала"
