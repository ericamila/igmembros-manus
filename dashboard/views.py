from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta
from members.models import Member
from churches.models import Church
from events.models import Event
from finances.models import Income, Expense # Importar Saida
from django.db import models # <<< ADICIONADO IMPORT
from django.db.models import Count, Sum, F # Importar Sum e F
from django.db.models.functions import TruncMonth, ExtractMonth, ExtractDay # Importar funções de data
import json
from itertools import chain # Para combinar querysets
from operator import attrgetter # Para ordenar lista combinada

@login_required
def index(request):
    # Obter data atual e datas para cálculos
    today = timezone.now().date()
    now = timezone.now() # Para usar em activity_type e evitar warning
    current_month = today.month
    first_day_current_month = today.replace(day=1)
    six_months_ago = first_day_current_month - relativedelta(months=5)# Primeiro dia de 6 meses atrás
    seven_days_ago = now - timedelta(days=7) # Usar datetime aware para comparação

    # Estatísticas para os cards
    total_members = Member.objects.count()
    total_churches = Church.objects.count()
    events_month = Event.objects.filter(date__gte=first_day_current_month, date__lte=today + timedelta(days=30)).count()
    
    
    # Calcular arrecadação mensal (card)
    income_current_month = Income.objects.filter(date__gte=first_day_current_month, date__lte=today)
    monthly_income = income_current_month.aggregate(total=Sum("amount"))["total"] or 0

    # Calcular despesas mensais (card)
    expenses_current_month = Expense.objects.filter(date__gte=first_day_current_month, date__lte=today)
    monthly_expense = expenses_current_month.aggregate(total=Sum("amount"))["total"] or 0
    
    # Próximos eventos (já existia, manter)
    upcoming_events = Event.objects.filter(date__gte=today).order_by("date", "time")[:5]

    # Aniversariantes do mês (já existia, manter)
    birthdays_month = Member.objects.filter(birth_date__month=current_month)\
                                        .annotate(day=ExtractDay("birth_date"))\
                                        .order_by("day", "name")

    # Atividades Recentes (CORRIGIDO)
    # Usar datetime aware (sete_dias_atras) para comparar com created_at/updated_at
    recent_members = Member.objects.filter(created_at__gte=seven_days_ago).annotate(activity_type=F("created_at"), type=models.Value("new_member", output_field=models.CharField()))
    recent_incomes = Income.objects.filter(created_at__gte=seven_days_ago).annotate(activity_type=F("created_at"), type=models.Value("income", output_field=models.CharField()))
    recent_expenses = Expense.objects.filter(created_at__gte=seven_days_ago).annotate(activity_type=F("created_at"), type=models.Value("expense", output_field=models.CharField()))
    recent_events_created = Event.objects.filter(created_at__gte=seven_days_ago).annotate(activity_type=F("created_at"), type=models.Value("event_created", output_field=models.CharField()))
    recent_events_updated = Event.objects.filter(updated_at__gte=seven_days_ago, updated_at__gt=F("created_at")).annotate(activity_type=F("updated_at"), type=models.Value("event_updated", output_field=models.CharField()))
    # Aniversários de hoje (para Atividade Recente) - Usar agora para activity_type
    birthdays_today = Member.objects.filter(birth_date__month=today.month, birth_date__day=today.day).annotate(activity_type=models.Value(now, output_field=models.DateTimeField()), type=models.Value("birthday", output_field=models.CharField()))

    # Combinar e ordenar atividades
    all_activities = sorted(
        chain(recent_members, recent_incomes, recent_expenses, recent_events_created, recent_events_updated, birthdays_today),
        key=attrgetter("activity_type"),
        reverse=True
    )[:5] # Limitar a 5 atividades recentes

    # Dados para o gráfico de membros por igreja
    members_per_church_qs = Church.objects.annotate(num_members=Count("members")).order_by("-num_members")
    labels_members_church = [church.name for church in members_per_church_qs]
    data_members_church = [church.num_members for church in members_per_church_qs]

    # Dados para o gráfico financeiro (últimos 6 meses)
    income_last_6_months = Income.objects.filter(
        date__gte=six_months_ago, date__lte=today
    ).annotate(
         month=TruncMonth("date")
    ).values("month").annotate(
        total_income=Sum("amount") # Updated aggregation
    ).order_by("month")

    expenses_last_6_months = Expense.objects.filter(
        date__gte=six_months_ago, date__lte=today
    ).annotate(
        month=TruncMonth("date")
    ).values("month").annotate(
        total_expense=Sum("amount") # Updated aggregation
    ).order_by("month")


    # Mapear dados por mês
    financial_data = {}
    months = [(six_months_ago + relativedelta(months=i)) for i in range(6)]
    labels_financial = [month.strftime("%b") for month in months] # Formato 'Abr', 'Mai', etc.

    for month in months:
        financial_data[month.strftime("%Y-%m")] = {"income": 0, "expense": 0}

    for income_entry in income_last_6_months:
        month_str = income_entry["month"].strftime("%Y-%m")
        if month_str in financial_data:
            financial_data[month_str]["income"] = float(income_entry["total_income"])

    for expense_entry in expenses_last_6_months:
        month_str = expense_entry["month"].strftime("%Y-%m")
        if month_str in financial_data:
            financial_data[month_str]["expense"] = float(expense_entry["total_expense"])


    data_income = [financial_data[month.strftime("%Y-%m")]["income"] for month in months]
    data_expense = [financial_data[month.strftime("%Y-%m")]["expense"] for month in months]

    context = {
        "active_menu": "dashboard",
        "total_members": total_members,
        "total_churches": total_churches,
        "events_month": events_month,
        "monthly_income": monthly_income, 
        "monthly_expense": monthly_expense,
        "upcoming_events": upcoming_events,
        "birthdays_month": birthdays_month,
        "recent_activities": all_activities,
        "labels_members_church": json.dumps(labels_members_church),
        "data_members_church": json.dumps(data_members_church),
        "labels_financial": json.dumps(labels_financial),
        "data_income": json.dumps(data_income), 
        "data_expense": json.dumps(data_expense), 
    }
    
    #print("Context data:", context)

    return render(request, "dashboard/index.html", context)


