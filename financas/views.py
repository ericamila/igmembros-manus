from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from .models import Entrada, Saida, Categoria
from .forms import EntradaForm, SaidaForm, CategoriaForm

@login_required
def entrada_list(request):
    entradas = Entrada.objects.all().order_by('-data')
    
    # Calcular totais
    total_entradas = Entrada.objects.aggregate(total=Sum('valor'))['total'] or 0
    total_saidas = Saida.objects.aggregate(total=Sum('valor'))['total'] or 0
    saldo = total_entradas - total_saidas
    
    # Entradas do mês atual
    hoje = timezone.now().date()
    primeiro_dia_mes = hoje.replace(day=1)
    entradas_mes = Entrada.objects.filter(data__gte=primeiro_dia_mes, data__lte=hoje)
    total_mes = sum(entrada.valor for entrada in entradas_mes)
    print(entradas)

    print(hoje)
    print(primeiro_dia_mes)
    print(entradas_mes)
    print(total_mes)
    
    return render(request, 'financas/entrada_list.html', {
        'entradas': entradas,
        'total_entradas': total_entradas,
        'total_saidas': total_saidas,
        'saldo': saldo,
        'total_mes': total_mes,
        'active_menu': 'financas',
    })

@login_required
def entrada_detail(request, pk):
    entrada = get_object_or_404(Entrada, pk=pk)
    return render(request, 'financas/entrada_detail.html', {
        'entrada': entrada,
        'active_menu': 'financas',
    })

@login_required
def entrada_create(request):
    if request.method == 'POST':
        form = EntradaForm(request.POST)
        if form.is_valid():
            entrada = form.save()
            messages.success(request, 'Entrada registrada com sucesso!')
            return redirect('financas:entrada_detail', pk=entrada.pk)
    else:
        form = EntradaForm()
    
    return render(request, 'financas/entrada_form.html', {
        'form': form,
        'title': 'Nova Entrada',
        'active_menu': 'financas',
    })

@login_required
def entrada_update(request, pk):
    entrada = get_object_or_404(Entrada, pk=pk)
    
    if request.method == 'POST':
        form = EntradaForm(request.POST, instance=entrada)
        if form.is_valid():
            form.save()
            messages.success(request, 'Entrada atualizada com sucesso!')
            return redirect('financas:entrada_detail', pk=entrada.pk)
    else:
        form = EntradaForm(instance=entrada)
    
    return render(request, 'financas/entrada_form.html', {
        'form': form,
        'entrada': entrada,
        'title': 'Editar Entrada',
        'active_menu': 'financas',
    })

@login_required
def entrada_delete(request, pk):
    entrada = get_object_or_404(Entrada, pk=pk)
    
    if request.method == 'POST':
        entrada.delete()
        messages.success(request, 'Entrada excluída com sucesso!')
        return redirect('financas:entrada_list')
    
    return render(request, 'financas/entrada_confirm_delete.html', {
        'entrada': entrada,
        'active_menu': 'financas',
    })

@login_required
def saida_list(request):
    saidas = Saida.objects.all().order_by('-data')
    print(saidas)
    # Calcular totais
    total_saidas = Saida.objects.aggregate(total=Sum('valor'))['total'] or 0
 
    # Saídas do mês atual
    hoje = timezone.now().date()
    primeiro_dia_mes = hoje.replace(day=1)
    saidas_mes = Saida.objects.filter(data__gte=primeiro_dia_mes, data__lte=hoje)
    total_mes = sum(saida.valor for saida in saidas_mes)
    
    return render(request, 'financas/saida_list.html', {
        'object_list': saidas,
        'total_saidas': total_saidas,
        'total_mes': total_mes,
        'active_menu': 'financas',
    })

@login_required
def saida_detail(request, pk):
    saida = get_object_or_404(Saida, pk=pk)
    return render(request, 'financas/saida_detail.html', {
        'saida': saida,
        'active_menu': 'financas',
    })

@login_required
def saida_create(request):
    if request.method == 'POST':
        form = SaidaForm(request.POST)
        if form.is_valid():
            saida = form.save()
            messages.success(request, 'Saída registrada com sucesso!')
            return redirect('financas:saida_detail', pk=saida.pk)
    else:
        form = SaidaForm()
    
    return render(request, 'financas/saida_form.html', {
        'form': form,
        'title': 'Nova Saída',
        'active_menu': 'financas',
    })

@login_required
def saida_update(request, pk):
    saida = get_object_or_404(Saida, pk=pk)
    
    if request.method == 'POST':
        form = SaidaForm(request.POST, instance=saida)
        if form.is_valid():
            form.save()
            messages.success(request, 'Saída atualizada com sucesso!')
            return redirect('financas:saida_detail', pk=saida.pk)
    else:
        form = SaidaForm(instance=saida)
    
    return render(request, 'financas/saida_form.html', {
        'form': form,
        'saida': saida,
        'title': 'Editar Saída',
        'active_menu': 'financas',
    })

@login_required
def saida_delete(request, pk):
    saida = get_object_or_404(Saida, pk=pk)
    
    if request.method == 'POST':
        saida.delete()
        messages.success(request, 'Saída excluída com sucesso!')
        return redirect('financas:saida_list')
    
    return render(request, 'financas/saida_confirm_delete.html', {
        'saida': saida,
        'active_menu': 'financas',
    })

@login_required
def categoria_list(request):
    categorias = Categoria.objects.all().order_by('nome')
    return render(request, 'financas/categoria_list.html', {
        'object_list': categorias,
        'active_menu': 'financas',
    })

@login_required
def categoria_create(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, 'Categoria criada com sucesso!')
            return redirect('financas:categoria_list')
    else:
        form = CategoriaForm()
    
    return render(request, 'financas/categoria_form.html', {
        'form': form,
        'title': 'Nova Categoria',
        'active_menu': 'financas',
    })

@login_required
def categoria_update(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria atualizada com sucesso!')
            return redirect('financas:categoria_list')
    else:
        form = CategoriaForm(instance=categoria)
    
    return render(request, 'financas/categoria_form.html', {
        'form': form,
        'categoria': categoria,
        'title': 'Editar Categoria',
        'active_menu': 'financas',
    })

@login_required
def categoria_delete(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    
    if request.method == 'POST':
        categoria.delete()
        messages.success(request, 'Categoria excluída com sucesso!')
        return redirect('financas:categoria_list')
    
    return render(request, 'financas/categoria_confirm_delete.html', {
        'categoria': categoria,
        'active_menu': 'financas',
    })

@login_required
def relatorio_financeiro(request):
    # Obter data atual e primeiro dia do mês
    hoje = timezone.now().date()
    primeiro_dia_mes = hoje.replace(day=1)
    
    # Entradas e saídas do mês atual
    entradas_mes = Entrada.objects.filter(data__gte=primeiro_dia_mes, data__lte=hoje)
    saidas_mes = Saida.objects.filter(data__gte=primeiro_dia_mes, data__lte=hoje)
    
    # Calcular totais
    total_entradas = sum(entrada.valor for entrada in entradas_mes)
    total_saidas = sum(saida.valor for saida in saidas_mes)
    saldo_mes = total_entradas - total_saidas
    
    # Entradas por categoria
    categorias = Categoria.objects.all()
    entradas_por_categoria = {}
    for categoria in categorias:
        valor = sum(entrada.valor for entrada in entradas_mes if entrada.categoria == categoria)
        if valor > 0:
            entradas_por_categoria[categoria.nome] = valor
    
    # Saídas por categoria
    saidas_por_categoria = {}
    for categoria in categorias:
        valor = sum(saida.valor for saida in saidas_mes if saida.categoria == categoria)
        if valor > 0:
            saidas_por_categoria[categoria.nome] = valor
    
    return render(request, 'financas/relatorio_financeiro.html', {
        'mes_atual': primeiro_dia_mes.strftime('%B/%Y'),
        'total_entradas': total_entradas,
        'total_saidas': total_saidas,
        'saldo_mes': saldo_mes,
        'entradas_por_categoria': entradas_por_categoria,
        'saidas_por_categoria': saidas_por_categoria,
        'entradas_mes': entradas_mes,
        'saidas_mes': saidas_mes,
        'active_menu': 'financas',
    })
