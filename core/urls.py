from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path


def admin_panel_redirect(_request):
    return redirect(f"{settings.FRONTEND_ORIGIN}/admin/")


urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", admin_panel_redirect),
    path("api/", include("api.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
