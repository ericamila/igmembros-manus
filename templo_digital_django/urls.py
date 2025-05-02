from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("dashboard.urls", namespace="dashboard")), # Rota raiz para o dashboard
    # Rotas para todos os apps
    path("igrejas/", include("churches.urls", namespace="churches")),
    path("membros/", include("members.urls", namespace="members")),
    path("financas/", include("finances.urls", namespace="finances")),
    path("eventos/", include("events.urls", namespace="evento")),
    path("escola/", include("school.urls", namespace="school")),
    path("usuarios/", include("users.urls", namespace="users")),
    path("relatorios/", include("reports.urls", namespace="reports")),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
