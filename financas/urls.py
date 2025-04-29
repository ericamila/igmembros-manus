from django.urls import path
from . import views

app_name = 'financas'

urlpatterns = [
    # Rotas para Entradas
    path('entradas/', views.entrada_list, name='entrada_list'),
    path('entradas/nova/', views.entrada_create, name='entrada_create'),
    path('entradas/<int:pk>/', views.entrada_detail, name='entrada_detail'),
    path('entradas/<int:pk>/editar/', views.entrada_update, name='entrada_update'),
    path('entradas/<int:pk>/excluir/', views.entrada_delete, name='entrada_delete'),
    
    # Rotas para Saídas
    path('saidas/', views.saida_list, name='saida_list'),
    path('saidas/nova/', views.saida_create, name='saida_create'),
    path('saidas/<int:pk>/', views.saida_detail, name='saida_detail'),
    path('saidas/<int:pk>/editar/', views.saida_update, name='saida_update'),
    path('saidas/<int:pk>/excluir/', views.saida_delete, name='saida_delete'),
    
    # Rotas para Categorias
    path('categorias/', views.categoria_list, name='categoria_list'),
    path('categorias/nova/', views.categoria_create, name='categoria_create'),
    path('categorias/<int:pk>/editar/', views.categoria_update, name='categoria_update'),
    path('categorias/<int:pk>/excluir/', views.categoria_delete, name='categoria_delete'),
    
    # Relatório Financeiro
    path('relatorio/', views.relatorio_financeiro, name='relatorio_financeiro'),
]
