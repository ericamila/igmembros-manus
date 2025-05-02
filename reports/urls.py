from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("", views.index, name="index"),
    path("movimentacoes-mensais/", views.relatorio_movimentacoes_mensais, name="movimentacoes_mensais"),
    path("dre/", views.relatorio_dre, name="dre"),
    path("balance/", views.relatorio_balanco, name="balanco"),
    path("school/alunos-por-turma/", views.relatorio_alunos_por_turma, name="alunos_por_turma"),
    path("school/frequencia/", views.relatorio_frequencia, name="frequencia"),
    path("members/estatisticas/", views.relatorio_members_estatisticas, name="members_estatisticas"),
    path("members/aniversariantes/", views.relatorio_aniversariantes, name="aniversariantes"),
    path("members/contribuicoes-anuais/", views.relatorio_contribuicoes_anuais, name="contribuicoes_anuais"),
]
