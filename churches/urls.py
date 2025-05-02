from django.urls import path
from . import views

app_name = 'churches'

urlpatterns = [
    path("", views.ChurchListView.as_view(), name="church_list"),
    path("<int:pk>/", views.ChurchDetailView.as_view(), name="church_detail"),
    path("novo/", views.ChurchCreateView.as_view(), name="church_add"),
    path("<int:pk>/edita/", views.ChurchUpdateView.as_view(), name="church_edit"),
    path("<int:pk>/excluir/", views.ChurchDeleteView.as_view(), name="church_delete"),
]

