from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("configuracao-igreja/", views.church_configuration_view, name="church_config"),
]

