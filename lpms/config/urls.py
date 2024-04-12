from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import TemplateView

urlpatterns = [
    path('', include('course.urls')),
    path('robots.txt', TemplateView.as_view(template_name='robots_txt.html')),
    path('admin/', admin.site.urls),
    path('users/', include('user.urls')),
    path('dashboard/', include('dashboard.urls')),
    path("__debug__/", include("debug_toolbar.urls")),
]

admin.site.site_header = "Панель администрирования LPMS"
admin.site.index_title = "LPMS | Администрирование портала"
