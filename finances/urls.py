from django.urls import path
from . import views

app_name = 'finances'

urlpatterns = [
    # Rotas para Entradas
    path('incomes/', views.income_list, name='income_list'),
    path('incomes/nova/', views.income_create, name='income_create'),
    path('incomes/<int:pk>/', views.income_detail, name='income_detail'),
    path('incomes/<int:pk>/editar/', views.income_update, name='income_update'),
    path('incomes/<int:pk>/excluir/', views.income_delete, name='income_delete'),
    
    # Rotas para Saídas
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/nova/', views.expense_create, name='expense_create'),
    path('expenses/<int:pk>/', views.expense_detail, name='expense_detail'),
    path('expenses/<int:pk>/editar/', views.expense_update, name='expense_update'),
    path('expenses/<int:pk>/excluir/', views.expense_delete, name='expense_delete'),
    
    # Rotas para Categorias
    path('categories/', views.category_list, name='category_list'),
    path('categories/nova/', views.category_create, name='category_create'),
    path('categories/<int:pk>/editar/', views.category_update, name='category_update'),
    path('categories/<int:pk>/excluir/', views.category_delete, name='category_delete'),
    
    # Relatório Financeiro
    path('report/', views.report_finance, name='report_finance'),
]
