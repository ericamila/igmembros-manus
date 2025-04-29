from django.urls import path
from . import views

app_name = "membros"

urlpatterns = [
    path("", views.MembroListView.as_view(), name="membro_list"),
    path("<int:pk>/", views.MembroDetailView.as_view(), name="membro_detail"),
    path("adicionar/", views.MembroCreateView.as_view(), name="membro_add"),
    path("<int:pk>/editar/", views.MembroUpdateView.as_view(), name="membro_edit"),
    path("<int:pk>/excluir/", views.MembroDeleteView.as_view(), name="membro_delete"),
]

