from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from membros.models import Member
from igrejas.models import Church
from escola.models import Student
from eventos.models import Event
from financas.models import Donation
from django.db.models import Sum, Count
from django.utils import timezone
import datetime

#@login_required # Descomentar quando a autenticação estiver implementada
def index(request):
    # Obter estatísticas (valores de exemplo, precisam ser calculados com base nos dados reais)
    total_membros = Member.objects.count()
    total_igrejas = Church.objects.count()
    total_alunos = Student.objects.count()
    
    # Eventos do mês atual
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    end_of_month = (start_of_month + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)
    eventos_mes = Event.objects.filter(date__range=[start_of_month, end_of_month]).count()

    # Arrecadação do mês atual (exemplo)
    arrecadacao_mes = Donation.objects.filter(month__year=today.year, month__month=today.month).aggregate(
        total_tithes=Sum("tithes"), 
        total_offerings=Sum("offerings"),
        total_projects=Sum("projects")
    )
    total_arrecadado = (arrecadacao_mes["total_tithes"] or 0) + \
                       (arrecadacao_mes["total_offerings"] or 0) + \
                       (arrecadacao_mes["total_projects"] or 0)

    # Atividades recentes (exemplo: últimos 5 membros adicionados)
    recent_activities = Member.objects.order_by("-created_at")[:5]

    # Próximos eventos (exemplo: próximos 5 eventos)
    upcoming_events = Event.objects.filter(date__gte=today).order_by("date", "time")[:5]

    context = {
        "total_membros": total_membros,
        "total_igrejas": total_igrejas,
        "total_alunos": total_alunos,
        "eventos_mes": eventos_mes,
        "total_arrecadado": total_arrecadado,
        "despesas_mes": 0, # Placeholder para despesas
        "recent_activities": recent_activities,
        "upcoming_events": upcoming_events,
        # Adicionar dados para gráficos (MembershipChart, DonationReport) se necessário
    }
    return render(request, "dashboard/index.html", context)

