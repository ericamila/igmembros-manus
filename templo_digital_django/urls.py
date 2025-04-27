from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls', namespace='dashboard')), # Rota raiz para o dashboard
    # Adicionar rotas para outros apps aqui:
    # path('igrejas/', include('igrejas.urls', namespace='igrejas')),
    # path('membros/', include('membros.urls', namespace='membros')),
    # path('financas/', include('financas.urls', namespace='financas')),
    # path('eventos/', include('eventos.urls', namespace='eventos')),
    # path('escola/', include('escola.urls', namespace='escola')),
    # path('contas/', include('django.contrib.auth.urls')), # Para autenticação
]

