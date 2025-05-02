from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("dashboard.urls", namespace="dashboard")), # Rota raiz para o dashboard
    # Rotas para todos os apps
    path("churches/", include("churches.urls", namespace="churches")),
    path("members/", include("members.urls", namespace="members")),
    path("finances/", include("finances.urls", namespace="finances")),
    path("events/", include("events.urls", namespace="evento")),
    path("school/", include("school.urls", namespace="school")),
    path("users/", include("users.urls", namespace="users")),
    path("reports/", include("reports.urls", namespace="reports")),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
