from django.urls import path
from . import views

app_name = 'finances'

urlpatterns = [
    # Rotas para Entradas
    path('entradas/', views.income_list, name='income_list'),
    path('entradas/nova/', views.income_create, name='income_create'),
    path('entradas/<int:pk>/', views.income_detail, name='income_detail'),
    path('entradas/<int:pk>/editar/', views.income_update, name='income_update'),
    path('entradas/<int:pk>/excluir/', views.income_delete, name='income_delete'),
    
    # Rotas para Saídas
    path('saidas/', views.expense_list, name='expense_list'),
    path('saidas/nova/', views.expense_create, name='expense_create'),
    path('saidas/<int:pk>/', views.expense_detail, name='expense_detail'),
    path('saidas/<int:pk>/editar/', views.expense_update, name='expense_update'),
    path('saidas/<int:pk>/excluir/', views.expense_delete, name='expense_delete'),
    
    # Rotas para Categorias
    path('categorias/', views.category_list, name='category_list'),
    path('categorias/nova/', views.category_create, name='category_create'),
    path('categorias/<int:pk>/editar/', views.category_update, name='category_update'),
    path('categorias/<int:pk>/excluir/', views.category_delete, name='category_delete'),
    
    # Relatório Financeiro
    path('relatorios/', views.report_finance, name='report_finance'),
]
