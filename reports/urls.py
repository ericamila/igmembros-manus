from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("", views.index, name="index"),

    # Financial Reports
    path("movimentacoes-mensais/", views.relatorio_movimentacoes_mensais, name="movimentacoes_mensais"),
    path("movimentacoes-mensais/export/xlsx/", views.export_movimentacoes_mensais_xlsx, name="export_movimentacoes_mensais_xlsx"), # Added export URL
    path("movimentacoes-mensais/export/pdf/", views.export_movimentacoes_mensais_pdf, name="export_movimentacoes_mensais_pdf"), # Added PDF export URL
    path("dre/", views.relatorio_dre, name="dre"),
    path("balance/", views.relatorio_balanco, name="balanco"),

    # Sunday School Reports
    path("school/alunos-por-turma/", views.relatorio_alunos_por_turma, name="alunos_por_turma"),
    path("school/frequencia/", views.relatorio_frequencia, name="frequencia"),

    # Members Reports
    path("membros/estatisticas/", views.relatorio_membros_estatisticas, name="membros_estatisticas"),
    path("members/aniversariantes/", views.relatorio_aniversariantes, name="aniversariantes"),
    path("members/contribuicoes-anuais/", views.relatorio_contribuicoes_anuais, name="contribuicoes_anuais"),

    # Accountability Reports 
    path("prestacao-contas/", views.AccountabilityReportListView.as_view(), name="accountability_list"),
    path("prestacao-contas/nova/", views.AccountabilityReportCreateView.as_view(), name="accountability_create"),
    path("prestacao-contas/<int:pk>/", views.AccountabilityReportDetailView.as_view(), name="accountability_detail"),
    path("prestacao-contas/<int:pk>/editar/", views.AccountabilityReportUpdateView.as_view(), name="accountability_update"),
    path("prestacao-contas/<int:pk>/excluir/", views.AccountabilityReportDeleteView.as_view(), name="accountability_delete"),
]
