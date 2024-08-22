from django.contrib import admin
from django.urls import include, path, re_path
from django.conf.urls.static import static
from django.views.generic.base import TemplateView

from config import settings


urlpatterns = [
    re_path(r"^accounts/", include("allauth.urls")),
    path('', include('course.urls')),
    path('robots.txt', TemplateView.as_view(template_name='robots_txt.html')),
    path('admin/', admin.site.urls),
    path('users/', include('user.urls')),
    path('dashboard/', include('dashboard.urls')),
    path("__debug__/", include("debug_toolbar.urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "Панель администрирования LPMS"
admin.site.index_title = "LPMS | Администрирование портала"
