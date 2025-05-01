from django.urls import path
from . import views

app_name = "relatorios"

urlpatterns = [
    path("", views.index, name="index"),
    path("movimentacoes-mensais/", views.relatorio_movimentacoes_mensais, name="movimentacoes_mensais"),
    path("dre/", views.relatorio_dre, name="dre"),
    path("balanco/", views.relatorio_balanco, name="balanco"),
    path("escola/alunos-por-turma/", views.relatorio_alunos_por_turma, name="alunos_por_turma"),
    path("escola/frequencia/", views.relatorio_frequencia, name="frequencia"),
    path("membros/estatisticas/", views.relatorio_membros_estatisticas, name="membros_estatisticas"),
    path("membros/aniversariantes/", views.relatorio_aniversariantes, name="aniversariantes"),
    path("membros/contribuicoes/", views.relatorio_contribuicoes_anuais, name="contribuicoes_anuais"),
]
