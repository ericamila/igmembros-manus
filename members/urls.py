from django.urls import path
from . import views

app_name = "members"

urlpatterns = [
    path("", views.MemberListView.as_view(), name="member_list"),
    path("<int:pk>/", views.MemberDetailView.as_view(), name="member_detail"),
    path("adicionar/", views.MemberCreateView.as_view(), name="member_add"),
    path("<int:pk>/editar/", views.MemberUpdateView.as_view(), name="member_edit"),
    path("<int:pk>/excluir/", views.MemberDeleteView.as_view(), name="member_delete"),
]

