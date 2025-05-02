from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('novo/', views.event_create, name='event_create'),
    path('<int:pk>/', views.event_detail, name='event_detail'),
    path('<int:pk>/editar/', views.event_update, name='event_update'),
    path('<int:pk>/excluir/', views.event_delete, name='event_delete'),
]
