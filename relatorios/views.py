from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from financas.models import Entrada, Saida, Categoria
from escola.models import SchoolClass, Student, Attendance
from membros.models import Member # Importar modelo de Membro
from django.utils import timezone
from datetime import date
from dateutil.relativedelta import relativedelta
from django.db.models import Sum, Count, Q, F, ExpressionWrapper, fields # Importar F, ExpressionWrapper, fields
from django.db.models.functions import ExtractMonth, ExtractDay # Para aniversariantes

@login_required
def index(request):
    context = {
        "active_menu": "relatorios",
    }
    return render(request, "relatorios/index.html", context)

# --- Relatórios Financeiros ---
# ... (código dos relatórios financeiros mantido) ...
@login_required
def relatorio_movimentacoes_mensais(request):
    hoje = timezone.now().date()
    mes_atual = hoje.month
    ano_atual = hoje.year

    # Permitir filtrar por mês e ano (GET parameters)
    try:
        mes_param = int(request.GET.get("mes", mes_atual))
        ano_param = int(request.GET.get("ano", ano_atual))
        data_filtro = date(ano_param, mes_param, 1)
    except (ValueError, TypeError):
        data_filtro = date(ano_atual, mes_atual, 1)

    primeiro_dia_mes = data_filtro
    ultimo_dia_mes = primeiro_dia_mes + relativedelta(months=1) - relativedelta(days=1)

    entradas = Entrada.objects.filter(data__gte=primeiro_dia_mes, data__lte=ultimo_dia_mes).order_by("data")
    saidas = Saida.objects.filter(data__gte=primeiro_dia_mes, data__lte=ultimo_dia_mes).order_by("data")

    total_entradas = sum(e.valor for e in entradas)
    total_saidas = sum(s.valor for s in saidas)
    saldo_mes = total_entradas - total_saidas

    # Gerar lista de meses/anos para o filtro dropdown
    anos_disponiveis = range(ano_atual, ano_atual - 5, -1) # Últimos 5 anos
    meses_disponiveis = [
        (1, "Janeiro"), (2, "Fevereiro"), (3, "Março"), (4, "Abril"),
        (5, "Maio"), (6, "Junho"), (7, "Julho"), (8, "Agosto"),
        (9, "Setembro"), (10, "Outubro"), (11, "Novembro"), (12, "Dezembro")
    ]

    context = {
        "active_menu": "relatorios",
        "entradas": entradas,
        "saidas": saidas,
        "total_entradas": total_entradas,
        "total_saidas": total_saidas,
        "saldo_mes": saldo_mes,
        "mes_selecionado": primeiro_dia_mes.month,
        "ano_selecionado": primeiro_dia_mes.year,
        "mes_nome": primeiro_dia_mes.strftime("%B"), # Nome do mês por extenso
        "anos_disponiveis": anos_disponiveis,
        "meses_disponiveis": meses_disponiveis,
    }
    return render(request, "relatorios/movimentacoes_mensais.html", context)

@login_required
def relatorio_dre(request):
    hoje = timezone.now().date()
    ano_atual = hoje.year

    # Permitir filtrar por ano (GET parameter)
    try:
        ano_param = int(request.GET.get("ano", ano_atual))
    except (ValueError, TypeError):
        ano_param = ano_atual

    primeiro_dia_ano = date(ano_param, 1, 1)
    ultimo_dia_ano = date(ano_param, 12, 31)

    # Agrupar entradas por categoria
    entradas_por_categoria = Entrada.objects.filter(
        data__gte=primeiro_dia_ano, data__lte=ultimo_dia_ano
    ).values("categoria__nome").annotate(total=Sum("valor")).order_by("-total")

    # Agrupar saídas por categoria
    saidas_por_categoria = Saida.objects.filter(
        data__gte=primeiro_dia_ano, data__lte=ultimo_dia_ano
    ).values("categoria__nome").annotate(total=Sum("valor")).order_by("-total")

    total_receitas = sum(item["total"] for item in entradas_por_categoria) or 0
    total_despesas = sum(item["total"] for item in saidas_por_categoria) or 0
    resultado_liquido = total_receitas - total_despesas

    # Gerar lista de anos para o filtro dropdown
    anos_disponiveis = range(ano_atual, ano_atual - 5, -1) # Últimos 5 anos

    context = {
        "active_menu": "relatorios",
        "ano_selecionado": ano_param,
        "entradas_por_categoria": entradas_por_categoria,
        "saidas_por_categoria": saidas_por_categoria,
        "total_receitas": total_receitas,
        "total_despesas": total_despesas,
        "resultado_liquido": resultado_liquido,
        "anos_disponiveis": anos_disponiveis,
    }
    return render(request, "relatorios/dre.html", context)

@login_required
def relatorio_balanco(request):
    # Para um balanço simplificado, calculamos o saldo acumulado até a data atual
    # Idealmente, um balanço real consideraria ativos e passivos específicos.
    # Aqui, focaremos no saldo de caixa acumulado.
    hoje = timezone.now().date()

    # Permitir filtrar por data (GET parameter)
    try:
        data_fim_str = request.GET.get("data_fim", hoje.strftime("%Y-%m-%d"))
        data_fim = date.fromisoformat(data_fim_str)
    except (ValueError, TypeError):
        data_fim = hoje

    total_entradas_acumulado = Entrada.objects.filter(data__lte=data_fim).aggregate(total=Sum("valor"))["total"] or 0
    total_saidas_acumulado = Saida.objects.filter(data__lte=data_fim).aggregate(total=Sum("valor"))["total"] or 0
    saldo_acumulado = total_entradas_acumulado - total_saidas_acumulado

    # Poderíamos adicionar outras contas de ativo/passivo aqui se o modelo suportasse
    ativos = {
        "Caixa/Banco (Saldo Acumulado)": saldo_acumulado,
    }
    passivos_patrimonio = {
        "Patrimônio Líquido (Resultado Acumulado)": saldo_acumulado, # Simplificação
    }

    context = {
        "active_menu": "relatorios",
        "data_fim": data_fim,
        "data_fim_str": data_fim.strftime("%Y-%m-%d"),
        "ativos": ativos,
        "passivos_patrimonio": passivos_patrimonio,
        "total_ativos": sum(ativos.values()),
        "total_passivos_patrimonio": sum(passivos_patrimonio.values()),
    }
    return render(request, "relatorios/balanco.html", context)

# --- Relatórios da Escola Dominical ---

@login_required
def relatorio_alunos_por_turma(request):
    turmas = SchoolClass.objects.annotate(num_alunos=Count("students")).order_by("name")
    total_alunos = Student.objects.count()

    context = {
        "active_menu": "relatorios",
        "turmas": turmas,
        "total_alunos": total_alunos,
    }
    return render(request, "relatorios/alunos_por_turma.html", context)

@login_required
def relatorio_frequencia(request):
    hoje = timezone.now().date()
    turmas = SchoolClass.objects.all().order_by("name")
    
    # Filtros
    turma_id = request.GET.get("turma_id")
    data_aula_str = request.GET.get("data_aula", hoje.strftime("%Y-%m-%d"))

    try:
        data_aula = date.fromisoformat(data_aula_str)
    except (ValueError, TypeError):
        data_aula = hoje

    frequencias = Attendance.objects.filter(date=data_aula).select_related("student__member")
    turma_selecionada = None
    if turma_id:
        try:
            turma_selecionada = SchoolClass.objects.get(pk=turma_id)
            frequencias = frequencias.filter(school_class_id=turma_id)
        except SchoolClass.DoesNotExist:
            turma_id = None # Reset se ID inválido
            
    frequencias = frequencias.order_by("student__member__name")

    total_presentes = frequencias.filter(present=True).count()
    total_ausentes = frequencias.filter(present=False).count()
    total_registros = frequencias.count()

    context = {
        "active_menu": "relatorios",
        "turmas": turmas,
        "turma_selecionada_id": turma_id,
        "turma_selecionada_nome": turma_selecionada.name if turma_selecionada else "Todas",
        "data_aula": data_aula,
        "data_aula_str": data_aula.strftime("%Y-%m-%d"),
        "frequencias": frequencias,
        "total_presentes": total_presentes,
        "total_ausentes": total_ausentes,
        "total_registros": total_registros,
    }
    return render(request, "relatorios/frequencia.html", context)

# --- Relatórios de Membros ---

@login_required
def relatorio_membros_estatisticas(request):
    total_membros = Member.objects.count()
    membros_ativos = Member.objects.filter(status="ativo").count()
    membros_por_status = Member.objects.values("status").annotate(count=Count("id")).order_by("-count")
    membros_por_genero = Member.objects.values("gender").annotate(count=Count("id")).order_by("-count")
    membros_por_estado_civil = Member.objects.values("marital_status").annotate(count=Count("id")).order_by("-count")
    membros_por_tipo = Member.objects.values("member_type").annotate(count=Count("id")).order_by("-count")

    # Mapear códigos para nomes legíveis (opcional, pode ser feito no template)
    status_map = dict(Member.STATUS_CHOICES)
    gender_map = dict(Member.GENDER_CHOICES)
    marital_map = dict(Member.MARITAL_STATUS_CHOICES)
    type_map = dict(Member.MEMBER_TYPE_CHOICES)

    context = {
        "active_menu": "relatorios",
        "total_membros": total_membros,
        "membros_ativos": membros_ativos,
        "membros_por_status": [(status_map.get(item["status"], item["status"]), item["count"]) for item in membros_por_status],
        "membros_por_genero": [(gender_map.get(item["gender"], item["gender"]), item["count"]) for item in membros_por_genero],
        "membros_por_estado_civil": [(marital_map.get(item["marital_status"], item["marital_status"]), item["count"]) for item in membros_por_estado_civil],
        "membros_por_tipo": [(type_map.get(item["member_type"], item["member_type"]), item["count"]) for item in membros_por_tipo],
    }
    return render(request, "relatorios/membros_estatisticas.html", context)

@login_required
def relatorio_aniversariantes(request):
    hoje = timezone.now().date()
    mes_atual = hoje.month

    # Permitir filtrar por mês (GET parameter)
    try:
        mes_param = int(request.GET.get("mes", mes_atual))
    except (ValueError, TypeError):
        mes_param = mes_atual

    aniversariantes = Member.objects.filter(birth_date__month=mes_param)\
                                    .annotate(dia=ExtractDay("birth_date"))\
                                    .order_by("dia", "name")

    meses_disponiveis = [
        (1, "Janeiro"), (2, "Fevereiro"), (3, "Março"), (4, "Abril"),
        (5, "Maio"), (6, "Junho"), (7, "Julho"), (8, "Agosto"),
        (9, "Setembro"), (10, "Outubro"), (11, "Novembro"), (12, "Dezembro")
    ]
    mes_nome = dict(meses_disponiveis).get(mes_param, "")

    context = {
        "active_menu": "relatorios",
        "aniversariantes": aniversariantes,
        "mes_selecionado": mes_param,
        "mes_nome": mes_nome,
        "meses_disponiveis": meses_disponiveis,
    }
    return render(request, "relatorios/aniversariantes.html", context)

# View para Relatório de Contribuições Anuais será adicionada aqui

