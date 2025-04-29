from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from membros.models import Member
from igrejas.models import Church
from eventos.models import Event
from financas.models import Entrada

@login_required
def index(request):
    # Obter data atual e primeiro dia do mês
    hoje = timezone.now().date()
    primeiro_dia_mes = hoje.replace(day=1)
    
    # Estatísticas para os cards
    total_membros = Member.objects.count()
    total_igrejas = Church.objects.count()
    eventos_mes = Event.objects.filter(date__gte=primeiro_dia_mes, date__lte=hoje + timedelta(days=30)).count()
    
    # Calcular arrecadação mensal
    entradas_mes = Entrada.objects.filter(data__gte=primeiro_dia_mes, data__lte=hoje)
    arrecadacao_mensal = sum(entrada.valor for entrada in entradas_mes)
    
    # Próximos eventos
    proximos_eventos = Event.objects.filter(date__gte=hoje).order_by('date', 'time')[:5]
    
    context = {
        'active_menu': 'dashboard',
        'total_membros': total_membros,
        'total_igrejas': total_igrejas,
        'eventos_mes': eventos_mes,
        'arrecadacao_mensal': arrecadacao_mensal,
        'proximos_eventos': proximos_eventos,
    }
    
    return render(request, 'dashboard/index.html', context)
