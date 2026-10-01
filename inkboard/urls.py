"""inkboard/urls.py"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import AdminLoginView
from core.media_views import protected_media_serve

handler403 = "core.views.custom_403"
handler404 = "core.views.custom_404"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("admin-login/", AdminLoginView.as_view(), name="admin_login"),
    path("accounts/", include("accounts.urls")),
    path("jobs/", include("jobs.urls")),
    path("applications/", include("applications.urls")),
    path("moderation/", include("moderation.urls")),
    path("media/<path:path>", protected_media_serve, name="protected_media"),
    path("", include("core.urls")),
]

