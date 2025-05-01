from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta
from membros.models import Member
from igrejas.models import Church
from eventos.models import Event
from financas.models import Entrada, Saida # Importar Saida
from django.db.models import Count, Sum, F # Importar Sum e F
from django.db.models.functions import TruncMonth # Importar TruncMonth
import json

@login_required
def index(request):
    # Obter data atual e datas para cálculos
    hoje = timezone.now().date()
    primeiro_dia_mes_atual = hoje.replace(day=1)
    seis_meses_atras = primeiro_dia_mes_atual - relativedelta(months=5) # Primeiro dia de 6 meses atrás

    # Estatísticas para os cards
    total_membros = Member.objects.count()
    total_igrejas = Church.objects.count()
    eventos_mes = Event.objects.filter(date__gte=primeiro_dia_mes_atual, date__lte=hoje + timedelta(days=30)).count()
    
    # Calcular arrecadação mensal (card)
    entradas_mes_atual = Entrada.objects.filter(data__gte=primeiro_dia_mes_atual, data__lte=hoje)
    arrecadacao_mensal = entradas_mes_atual.aggregate(total=Sum("valor"))["total"] or 0
    
    # Próximos eventos
    proximos_eventos = Event.objects.filter(date__gte=hoje).order_by("date", "time")[:5]

    # Dados para o gráfico de membros por igreja
    membros_por_igreja_qs = Church.objects.annotate(num_membros=Count("members")).order_by("-num_membros")
    labels_membros_igreja = [igreja.name for igreja in membros_por_igreja_qs]
    data_membros_igreja = [igreja.num_membros for igreja in membros_por_igreja_qs]

    # Dados para o gráfico financeiro (últimos 6 meses)
    entradas_ultimos_6_meses = Entrada.objects.filter(
        data__gte=seis_meses_atras, data__lte=hoje
    ).annotate(
        mes=TruncMonth("data")
    ).values("mes").annotate(
        total_entrada=Sum("valor")
    ).order_by("mes")

    saidas_ultimos_6_meses = Saida.objects.filter(
        data__gte=seis_meses_atras, data__lte=hoje
    ).annotate(
        mes=TruncMonth("data")
    ).values("mes").annotate(
        total_saida=Sum("valor")
    ).order_by("mes")

    # Mapear dados por mês
    dados_financeiros = {}
    meses = [(seis_meses_atras + relativedelta(months=i)) for i in range(6)]
    labels_financeiro = [mes.strftime("%b") for mes in meses] # Formato 'Abr', 'Mai', etc.

    for mes in meses:
        dados_financeiros[mes.strftime("%Y-%m")] = {"entrada": 0, "saida": 0}

    for entrada in entradas_ultimos_6_meses:
        mes_str = entrada["mes"].strftime("%Y-%m")
        if mes_str in dados_financeiros:
            dados_financeiros[mes_str]["entrada"] = float(entrada["total_entrada"])

    for saida in saidas_ultimos_6_meses:
        mes_str = saida["mes"].strftime("%Y-%m")
        if mes_str in dados_financeiros:
            dados_financeiros[mes_str]["saida"] = float(saida["total_saida"])

    data_entradas = [dados_financeiros[mes.strftime("%Y-%m")]["entrada"] for mes in meses]
    data_saidas = [dados_financeiros[mes.strftime("%Y-%m")]["saida"] for mes in meses]

    context = {
        "active_menu": "dashboard",
        "total_membros": total_membros,
        "total_igrejas": total_igrejas,
        "eventos_mes": eventos_mes,
        "arrecadacao_mensal": arrecadacao_mensal,
        "proximos_eventos": proximos_eventos,
        "labels_membros_igreja": json.dumps(labels_membros_igreja),
        "data_membros_igreja": json.dumps(data_membros_igreja),
        "labels_financeiro": json.dumps(labels_financeiro),
        "data_entradas": json.dumps(data_entradas),
        "data_saidas": json.dumps(data_saidas),
    }
    
    return render(request, "dashboard/index.html", context)

