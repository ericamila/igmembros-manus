from django.urls import path
from . import views

app_name = 'igrejas'

urlpatterns = [
    path('', views.IgrejaListView.as_view(), name='igreja_list'),
    path('<int:pk>/', views.IgrejaDetailView.as_view(), name='igreja_detail'),
    path('adicionar/', views.IgrejaCreateView.as_view(), name='igreja_add'),
    path('<int:pk>/editar/', views.IgrejaUpdateView.as_view(), name='igreja_edit'),
    path('<int:pk>/excluir/', views.IgrejaDeleteView.as_view(), name='igreja_delete'),
]

