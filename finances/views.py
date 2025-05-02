from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from .models import Income, Expense, Category
from .forms import IncomeForm, ExpenseForm, CategoryForm

@login_required
def income_list(request):
    incomes = Income.objects.all().order_by('-date')
    
    # Calcular totais
    total_incomes = Income.objects.aggregate(total=Sum('amount'))['total'] or 0
    total_expenses = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0
    balance = total_incomes - total_expenses
    
    # Entradas do mês atual
    today = timezone.now().date()
    first_day_month = today.replace(day=1)
    incomes_month = Income.objects.filter(date__gte=first_day_month, date__lte=today)
    total_month_income = sum(income.amount for income in incomes_month)

    return render(request, 'finances/income_list.html', {
        "incomes": incomes, 
        "total_incomes": total_incomes,
        "total_expenses": total_expenses,
        "balance": balance, 
        "total_month_income": total_month_income, 
        "active_menu": "finances", 
    })

@login_required
def income_detail(request, pk):
    income = get_object_or_404(Income, pk=pk)
    return render(request, 'finances/income_detail.html', {
        'income': income,
        'active_menu': 'finances',
    })

@login_required
def income_create(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST, request.FILES)
        if form.is_valid():
            income = form.save()
            messages.success(request, 'Entrada registrada com sucesso!')
            return redirect('finances:income_detail', pk=income.pk)
    else:
        form = IncomeForm()
    
    return render(request, 'finances/income_form.html', {
        'form': form,
        'title': 'Nova Entrada',
        'active_menu': 'finances',
    })

@login_required
def income_update(request, pk):
    income = get_object_or_404(Income, pk=pk)
    
    if request.method == 'POST':
        form = IncomeForm(request.POST, request.FILES, instance=income)
        if form.is_valid():
            form.save()
            messages.success(request, 'Entrada atualizada com sucesso!')
            return redirect('finances:income_detail', pk=income.pk)
    else:
        form = IncomeForm(instance=income)
    
    return render(request, 'finances/income_form.html', {
        'form': form,
        'income': income,
        'title': 'Editar Entrada',
        'active_menu': 'finances',
    })

@login_required
def income_delete(request, pk):
    income = get_object_or_404(Income, pk=pk)
    
    if request.method == 'POST':
        income.delete()
        messages.success(request, 'Entrada excluída com sucesso!')
        return redirect('finances:income_list')
    
    return render(request, 'finances/income_confirm_delete.html', {
        'income': income,
        'active_menu': 'finances',
    })

@login_required
def expense_list(request):
    expenses = Expense.objects.all().order_by('-date')
    # Calcular totais
    total_expenses = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0
 
    # Saídas do mês atual
    today = timezone.now().date()
    first_day_month = today.replace(day=1)
    expenses_month = Expense.objects.filter(date__gte=first_day_month, date__lte=today)
    total_month_expense = sum(expense.amount for expense in expenses_month)
    
    return render(request, 'finances/expense_list.html', {
        "expenses": expenses, 
        "total_expenses": total_expenses,
        "total_month_expense": total_month_expense, 
        "active_menu": "finances",
    })

@login_required
def expense_detail(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    return render(request, 'finances/expense_detail.html', {
        'expense': expense,
        'active_menu': 'finances',
    })

@login_required
def expense_create(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save()
            messages.success(request, 'Saída registrada com sucesso!')
            return redirect('finances:expense_detail', pk=expense.pk)
    else:
        form = ExpenseForm()
    
    return render(request, 'finances/expense_form.html', {
        'form': form,
        'title': 'Nova Saída',
        'active_menu': 'finances',
    })

@login_required
def expense_update(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, 'Saída atualizada com sucesso!')
            return redirect('finances:expense_detail', pk=expense.pk)
    else:
        form = ExpenseForm(instance=expense)
    
    return render(request, 'finances/expense_form.html', {
        'form': form,
        'expense': expense,
        'title': 'Editar Saída',
        'active_menu': 'finances',
    })

@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Saída excluída com sucesso!')
        return redirect('finances:expense_list')
    
    return render(request, 'finances/expense_confirm_delete.html', {
        'expense': expense,
        'active_menu': 'finances',
    })

@login_required
def category_list(request):
    categorys = Category.objects.all().order_by('name')
    return render(request, 'finances/category_list.html', {
        'object_list': categorys,
        'active_menu': 'finances',
    })

@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, 'Categoria criada com sucesso!')
            return redirect('finances:category_list')
    else:
        form = CategoryForm()
    
    return render(request, 'finances/category_form.html', {
        'form': form,
        'title': 'Nova Categoria',
        'active_menu': 'finances',
    })

@login_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria atualizada com sucesso!')
            return redirect('finances:category_list')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'finances/category_form.html', {
        'form': form,
        'category': category,
        'title': 'Editar Categoria',
        'active_menu': 'finances',
    })

@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Categoria excluída com sucesso!')
        return redirect('finances:category_list')
    
    return render(request, 'finances/category_confirm_delete.html', {
        'category': category,
        'active_menu': 'finances',
    })

# remanejar abaixo para relatorio financeiro
@login_required
def report_finance(request):
    # Obter date atual e primeiro dia do mês
    hoje = timezone.now().date()
    primeiro_dia_mes = hoje.replace(day=1)
    
    # Incomes e saídas do mês atual
    incomes_mes = Income.objects.filter(date__gte=primeiro_dia_mes, date__lte=hoje)
    expenses_mes = Expense.objects.filter(date__gte=primeiro_dia_mes, date__lte=hoje)
    
    # Calcular totais
    total_incomes = sum(income.amount for income in incomes_mes)
    total_expenses = sum(expense.amount for expense in expenses_mes)
    saldo_mes = total_incomes - total_expenses
    
    # Entradas por category
    categorys = Category.objects.all()
    incomes_por_category = {}
    for category in categorys:
        amount = sum(income.amount for income in incomes_mes if income.category == category)
        if amount > 0:
            incomes_por_category[category.name] = amount
    
    # Saídas por category
    expenses_por_category = {}
    for category in categorys:
        amount = sum(expense.amount for expense in expenses_mes if expense.category == category)
        if amount > 0:
            expenses_por_category[category.name] = amount
    
    return render(request, 'finances/report_finance.html', {
        'mes_atual': primeiro_dia_mes.strftime('%B/%Y'),
        'total_incomes': total_incomes,
        'total_expenses': total_expenses,
        'saldo_mes': saldo_mes,
        'incomes_por_category': incomes_por_category,
        'expenses_por_category': expenses_por_category,
        'incomes_mes': incomes_mes,
        'expenses_mes': expenses_mes,
        'active_menu': 'finances',
    })
