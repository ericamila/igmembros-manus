from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("", views.index, name="index"),

    # Financial Reports
    path("movimentacoes-mensais/", views.relatorio_movimentacoes_mensais, name="movimentacoes_mensais"),
    path("movimentacoes-mensais/export/xlsx/", views.export_movimentacoes_mensais_xlsx, name="export_movimentacoes_mensais_xlsx"),
    path("movimentacoes-mensais/export/pdf/", views.export_movimentacoes_mensais_pdf, name="export_movimentacoes_mensais_pdf"),
    path("dre/", views.relatorio_dre, name="dre"),
    path("dre/export/xlsx/", views.export_dre_xlsx, name="export_dre_xlsx"),
    path("dre/export/pdf/", views.export_dre_pdf, name="export_dre_pdf"),
    path("balance/", views.relatorio_balanco, name="balanco"),
    path("balance/export/xlsx/", views.export_balanco_xlsx, name="export_balanco_xlsx"),
    path("balance/export/pdf/", views.export_balanco_pdf, name="export_balanco_pdf"),
    path("financeiro-categorias/", views.relatorio_financeiro_categorias, name="financeiro_categorias"), # Added Categoria report URL

    # Sunday School Reports
    path("school/alunos-por-turma/", views.relatorio_alunos_por_turma, name="alunos_por_turma"),
    path("school/alunos-por-turma/export/xlsx/", views.export_alunos_por_turma_xlsx, name="export_alunos_por_turma_xlsx"),
    path("school/alunos-por-turma/export/pdf/", views.export_alunos_por_turma_pdf, name="export_alunos_por_turma_pdf"),
    path("school/frequencia/", views.relatorio_frequencia, name="frequencia"),
    path("school/frequencia/export/xlsx/", views.export_frequencia_xlsx, name="export_frequencia_xlsx"),
    path("school/frequencia/export/pdf/", views.export_frequencia_pdf, name="export_frequencia_pdf"),

    # Members Reports
    path("membros/estatisticas/", views.relatorio_membros_estatisticas, name="membros_estatisticas"),
    path("membros/estatisticas/export/xlsx/", views.export_membros_estatisticas_xlsx, name="export_membros_estatisticas_xlsx"),
    path("membros/estatisticas/export/pdf/", views.export_membros_estatisticas_pdf, name="export_membros_estatisticas_pdf"),
    path("members/aniversariantes/", views.relatorio_aniversariantes, name="aniversariantes"),
    path("members/contribuicoes-anuais/", views.relatorio_contribuicoes_anuais, name="contribuicoes_anuais"),

    # Accountability Reports 
    path("prestacao-contas/", views.AccountabilityReportListView.as_view(), name="accountability_list"),
    path("prestacao-contas/nova/", views.AccountabilityReportCreateView.as_view(), name="accountability_create"),
    path("prestacao-contas/<int:pk>/", views.AccountabilityReportDetailView.as_view(), name="accountability_detail"),
    path("prestacao-contas/<int:pk>/editar/", views.AccountabilityReportUpdateView.as_view(), name="accountability_update"),
    path("prestacao-contas/<int:pk>/excluir/", views.AccountabilityReportDeleteView.as_view(), name="accountability_delete"),
]

