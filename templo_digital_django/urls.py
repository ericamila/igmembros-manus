from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("dashboard.urls", namespace="dashboard")), # Rota raiz para o dashboard
    # Rotas para todos os apps
    path("igrejas/", include("igrejas.urls", namespace="igrejas")),
    path("membros/", include("membros.urls", namespace="membros")),
    path("financas/", include("financas.urls", namespace="financas")),
    path("eventos/", include("eventos.urls", namespace="eventos")),
    path("escola/", include("escola.urls", namespace="escola")),
    path("usuarios/", include("usuarios.urls", namespace="usuarios")),
    path("relatorios/", include("relatorios.urls", namespace="relatorios")),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
