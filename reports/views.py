from decimal import Decimal
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.db import transaction # Import transaction

# Updated model imports
from finances.models import Income, Expense
from school.models import SchoolClass, Student, Attendance
from members.models import Member
from django.utils import timezone
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from django.db.models import Sum, Count
from django.db.models.functions import ExtractDay, TruncYear

# Import new models and forms for Accountability
from .models import AccountabilityReport, AccountabilityDocument
from .forms import AccountabilityReportForm, AccountabilityDocumentFormSet

# Imports for Export
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
import io

@login_required
def index(request):
    context = {
        "active_menu": "reports",
    }
    return render(request, "reports/index.html", context)

# --- Helper function to get common context for reports ---
def _get_report_filters(request):
    today = timezone.now().date()
    current_month = today.month
    current_year = today.year

    try:
        month_param = int(request.GET.get("month", current_month))
        year_param = int(request.GET.get("year", current_year))
        filter_date = date(year_param, month_param, 1)
    except (ValueError, TypeError):
        month_param = current_month
        year_param = current_year
        filter_date = date(current_year, current_month, 1)

    try:
        end_date_str = request.GET.get("end_date", today.strftime("%Y-%m-%d"))
        end_date = date.fromisoformat(end_date_str)
    except (ValueError, TypeError):
        end_date = today
        end_date_str = end_date.strftime("%Y-%m-%d")

    class_id = request.GET.get("class_id")
    try:
        class_date_str = request.GET.get("class_date", today.strftime("%Y-%m-%d"))
        class_date = date.fromisoformat(class_date_str)
    except (ValueError, TypeError):
        class_date = today
        class_date_str = class_date.strftime("%Y-%m-%d")

    member_param = request.GET.get("member")

    return {
        "today": today,
        "current_month": current_month,
        "current_year": current_year,
        "month_param": month_param,
        "year_param": year_param,
        "filter_date": filter_date,
        "end_date": end_date,
        "end_date_str": end_date_str,
        "class_id": class_id,
        "class_date": class_date,
        "class_date_str": class_date_str,
        "member_param": member_param,
    }


# --- Relatórios Financeiros ---
@login_required
def relatorio_movimentacoes_mensais(request):
    filters = _get_report_filters(request)
    first_day_month = filters["filter_date"]
    last_day_month = first_day_month + relativedelta(months=1) - relativedelta(days=1)
    
    incomes = Income.objects.filter(date__gte=first_day_month, date__lte=last_day_month).order_by("date")
    expenses = Expense.objects.filter(date__gte=first_day_month, date__lte=last_day_month).order_by("date")

    total_incomes = sum(i.amount for i in incomes)
    total_expenses = sum(e.amount for e in expenses)
    month_balance = total_incomes - total_expenses

    # Gerar lista de meses/anos para o filtro dropdown
    available_years = range(filters["current_year"], filters["current_year"] - 5, -1) # Últimos 5 anos
    available_months = [
        (1, "Janeiro"), (2, "Fevereiro"), (3, "Março"), (4, "Abril"),
        (5, "Maio"), (6, "Junho"), (7, "Julho"), (8, "Agosto"),
        (9, "Setembro"), (10, "Outubro"), (11, "Novembro"), (12, "Dezembro")
    ]

    context = {
        "active_menu": "reports",
        "incomes": incomes, 
        "expenses": expenses, 
        "total_incomes": total_incomes, 
        "total_expenses": total_expenses, 
        "month_balance": month_balance, 
        "selected_month": first_day_month.month, 
        "selected_year": first_day_month.year, 
        "month_name": first_day_month.strftime("%B"), # Nome do mês por extenso
        "available_years": available_years,
        "available_months": available_months,
        "filters_query_string": request.GET.urlencode(), # Pass filters for export links
    }
    return render(request, "reports/movimentacoes_mensais.html", context)


@login_required
def export_movimentacoes_mensais_xlsx(request):
    filters = _get_report_filters(request)
    first_day_month = filters["filter_date"]
    last_day_month = first_day_month + relativedelta(months=1) - relativedelta(days=1)

    incomes = Income.objects.filter(date__gte=first_day_month, date__lte=last_day_month).order_by("date")
    expenses = Expense.objects.filter(date__gte=first_day_month, date__lte=last_day_month).order_by("date")
    total_incomes = sum(i.amount for i in incomes)
    total_expenses = sum(e.amount for e in expenses)
    month_balance = total_incomes - total_expenses

    wb = Workbook()
    ws = wb.active
    ws.title = f"Mov. {first_day_month.strftime('%b_%Y')}"

    # Title
    ws.merge_cells("A1:E1")
    title_cell = ws["A1"]
    title_cell.value = f"Relatório de Movimentações Mensais - {first_day_month.strftime('%B %Y')}"
    title_cell.font = Font(bold=True, size=14)
    title_cell.alignment = Alignment(horizontal="center")
    ws.row_dimensions[1].height = 20

    # Incomes Section
    ws.append([]) # Spacer row
    ws.append(["Receitas"])
    ws["A3"].font = Font(bold=True, size=12)
    ws.append(["Data", "Descrição", "Categoria", "Membro", "Valor"])
    header_font = Font(bold=True)
    for col in ["A", "B", "C", "D", "E"]:
        ws[f"{col}4"].font = header_font

    row = 5
    for income in incomes:
        ws.append([
            income.date,
            income.description,
            income.category.name if income.category else "",
            income.member.name if income.member else "",
            income.amount
        ])
        ws[f"E{row}"].number_format = "R$ #,##0.00"
        row += 1

    ws.append(["", "", "", "Total Receitas:", total_incomes])
    ws[f"D{row}"].font = Font(bold=True)
    ws[f"E{row}"].font = Font(bold=True)
    ws[f"E{row}"].number_format = "R$ #,##0.00"
    row += 1

    # Expenses Section
    ws.append([]) # Spacer row
    row += 1
    ws.append(["Despesas"])
    ws[f"A{row}"].font = Font(bold=True, size=12)
    row += 1
    ws.append(["Data", "Descrição", "Categoria", "", "Valor"])
    for col in ["A", "B", "C", "E"]:
        ws[f"{col}{row}"].font = header_font
    row += 1

    for expense in expenses:
        ws.append([
            expense.date,
            expense.description,
            expense.category.name if expense.category else "",
            "",
            expense.amount
        ])
        ws[f"E{row}"].number_format = "R$ #,##0.00"
        row += 1

    ws.append(["", "", "", "Total Despesas:", total_expenses])
    ws[f"D{row}"].font = Font(bold=True)
    ws[f"E{row}"].font = Font(bold=True)
    ws[f"E{row}"].number_format = "R$ #,##0.00"
    row += 1

    # Balance Section
    ws.append([]) # Spacer row
    row += 1
    ws.append(["", "", "", "Saldo do Mês:", month_balance])
    ws[f"D{row}"].font = Font(bold=True, size=12)
    ws[f"E{row}"].font = Font(bold=True, size=12)
    ws[f"E{row}"].number_format = "R$ #,##0.00"

    # Adjust column widths
    ws.column_dimensions["A"].width = 12
    ws.column_dimensions["B"].width = 35
    ws.column_dimensions["C"].width = 20
    ws.column_dimensions["D"].width = 20
    ws.column_dimensions["E"].width = 15

    # Save to buffer
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    response = HttpResponse(
        buffer,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f"attachment; filename=movimentacoes_{first_day_month.strftime('%Y_%m')}.xlsx"
    return response

@login_required
def relatorio_dre(request):
    filters = _get_report_filters(request)
    year_param = filters["year_param"]
    first_day_year = date(year_param, 1, 1)
    last_day_year = date(year_param, 12, 31)

    # Agrupar entradas por categoria
    incomes_by_category = Income.objects.filter(
        date__gte=first_day_year, date__lte=last_day_year
    ).values("category__name").annotate(total=Sum("amount")).order_by("-total")

    # Agrupar saídas por categoria
    expenses_by_category = Expense.objects.filter(
        date__gte=first_day_year, date__lte=last_day_year
    ).values("category__name").annotate(total=Sum("amount")).order_by("-total")

    total_revenue = sum(item["total"] for item in incomes_by_category) or 0
    total_expenditure = sum(item["total"] for item in expenses_by_category) or 0
    net_result = total_revenue - total_expenditure

    # Gerar lista de anos para o filtro dropdown
    available_years = range(filters["current_year"], filters["current_year"] - 5, -1) # Últimos 5 anos

    context = {
        "active_menu": "reports",
        "selected_year": year_param,
        "incomes_by_category": incomes_by_category, 
        "expenses_by_category": expenses_by_category, 
        "total_revenue": total_revenue, 
        "total_expenditure": total_expenditure, 
        "net_result": net_result, 
        "available_years": available_years,
        "filters_query_string": request.GET.urlencode(), # Pass filters for export links

    }
    return render(request, "reports/dre.html", context)

@login_required
def relatorio_balanco(request):
    # Para um balanço simplificado, calculamos o saldo acumulado até a date atual
    # Idealmente, um balanço real consideraria ativos e passivos específicos.
    # Aqui, focaremos no saldo de caixa acumulado.
    filters = _get_report_filters(request)
    end_date = filters["end_date"]

    total_incomes_accumulated = Income.objects.filter(date__lte=end_date).aggregate(total=Sum("amount"))["total"] or 0
    total_expenses_accumulated = Expense.objects.filter(date__lte=end_date).aggregate(total=Sum("amount"))["total"] or 0
    accumulated_balance = total_incomes_accumulated - total_expenses_accumulated

    # Poderíamos adicionar outras contas de ativo/passivo aqui se o modelo suportasse
    assets = {
        "Caixa/Banco (Saldo Acumulado)": accumulated_balance,
    }
    liabilities_equity = {
        "Patrimônio Líquido (Resultado Acumulado)": accumulated_balance, # Simplificação
    }

    context = {
        "active_menu": "reports",
        "end_date": end_date, 
        "end_date_str": filters["end_date_str"],
        "assets": assets,
        "liabilities_equity": liabilities_equity, 
        "total_assets": sum(assets.values()),
        "total_liabilities_equity": sum(liabilities_equity.values()), 
        "filters_query_string": request.GET.urlencode(), # Pass filters for export links
    }
    return render(request, "reports/balanco.html", context)

# --- Relatórios da Escola Dominical ---

@login_required
def relatorio_alunos_por_turma(request):
    classes = SchoolClass.objects.annotate(num_students=Count("students")).order_by("name")
    total_students = Student.objects.count()

    context = {
        "active_menu": "reports",
        "classes": classes, 
        "total_students": total_students,
    }
    return render(request, "reports/alunos_por_turma.html", context)

@login_required
def relatorio_frequencia(request):
    filters = _get_report_filters(request)
    class_id = filters["class_id"]
    class_date = filters["class_date"]

    classes = SchoolClass.objects.all().order_by("name")
    attendances = Attendance.objects.filter(date=class_date).select_related("student__member")
    selected_class = None
    if class_id:
        try:
            selected_class = SchoolClass.objects.get(pk=class_id)
            attendances = attendances.filter(school_class_id=class_id)
        except SchoolClass.DoesNotExist:
            class_id = None

    attendances = attendances.order_by("student__member__name")
    total_present = attendances.filter(present=True).count()
    total_absent = attendances.filter(present=False).count()
    total_records = attendances.count()

    context = {
        "active_menu": "reports",
        "classes": classes,
        "selected_class_id": class_id,
        "selected_class_name": selected_class.name if selected_class else "Todas",
        "class_date": class_date,
        "class_date_str": filters["class_date_str"],
        "attendances": attendances,
        "total_present": total_present,
        "total_absent": total_absent,
        "total_records": total_records,
        "filters_query_string": request.GET.urlencode(), # Pass filters for export links
    }
    return render(request, "reports/frequencia.html", context)

# --- Relatórios de Membros ---

@login_required
def relatorio_membros_estatisticas(request):
    total_members = Member.objects.count()
    active_members = Member.objects.filter(status="active").count() # Changed filter value
    members_by_status = Member.objects.values("status").annotate(count=Count("id")).order_by("-count")
    members_by_gender = Member.objects.values("gender").annotate(count=Count("id")).order_by("-count")
    members_by_marital_status = Member.objects.values("marital_status").annotate(count=Count("id")).order_by("-count")
    members_by_type = Member.objects.values("member_type").annotate(count=Count("id")).order_by("-count")

    # Mapear códigos para nomes legíveis (opcional, pode ser feito no template)
    status_map = dict(Member.STATUS_CHOICES)
    gender_map = dict(Member.GENDER_CHOICES)
    marital_map = dict(Member.MARITAL_STATUS_CHOICES)
    type_map = dict(Member.MEMBER_TYPE_CHOICES)

    context = {
        "active_menu": "reports",
        "total_members": total_members,
        "active_members": active_members, 
        "members_by_status": [(status_map.get(item["status"], item["status"]), item["count"]) for item in members_by_status],
        "members_by_gender": [(gender_map.get(item["gender"], item["gender"]), item["count"]) for item in members_by_gender],
        "members_by_marital_status": [(marital_map.get(item["marital_status"], item["marital_status"]), item["count"]) for item in members_by_marital_status],
        "members_by_type": [(type_map.get(item["member_type"], item["member_type"]), item["count"]) for item in members_by_type],
    }
    return render(request, "reports/members_estatisticas.html", context)

@login_required
def relatorio_aniversariantes(request):
    today = timezone.now().date()
    current_month = today.month

    # Permitir filtrar por mês (GET parameter)
    try:
        month_param = int(request.GET.get("month", current_month))
    except (ValueError, TypeError):
        month_param = current_month

    birthdays = Member.objects.filter(birth_date__month=month_param)\
                                    .annotate(day=ExtractDay("birth_date"))\
                                    .order_by("day", "name")
    
    available_months = [
        (1, "Janeiro"), (2, "Fevereiro"), (3, "Março"), (4, "Abril"),
        (5, "Maio"), (6, "Junho"), (7, "Julho"), (8, "Agosto"),
        (9, "Setembro"), (10, "Outubro"), (11, "Novembro"), (12, "Dezembro")
    ]
    month_name = dict(available_months).get(month_param, "")

    context = {
        "active_menu": "reports",
        "birthdays": birthdays, 
        "selected_month": month_param,
        "month_name": month_name,
        "available_months": available_months,
    }
    return render(request, "reports/aniversariantes.html", context)

@login_required
def relatorio_contribuicoes_anuais(request):
    today = timezone.now().date()
    current_year = today.year
    all_members = Member.objects.filter(status='ativo').order_by('name') # Get active members for filter

    # Permitir filtrar por ano e membro (GET parameter)
    try:
        year_param = int(request.GET.get("year", current_year))
    except (ValueError, TypeError):
        year_param = current_year
        
    member_param = request.GET.get("member") # Get member ID from filter

    # Filtrar entradas do ano que estão associadas a um membro
    contributions_query = Income.objects.filter(
        date__year=year_param,
        member__isnull=False
    )

    selected_member_instance = None
    if member_param:
        try:
            selected_member_instance = Member.objects.get(pk=member_param)
            contributions_query = contributions_query.filter(member_id=member_param)
        except Member.DoesNotExist:
            member_param = None # Reset if invalid member ID

   # Group by member ID and name, sum the amount
    contributions = contributions_query.values(
        "member__id", "member__name" 
    ).annotate(
        total_contribution=Sum("amount") # Updated field name
    ).order_by("-total_contribution", "member__name") # Order by highest contribution

    # Calculate overall total only if no specific member is selected
    total_overall_contribution = None
    if not member_param:
        total_overall_contribution = contributions.aggregate(total_overall=Sum("total_contribution"))["total_overall"] or 0

    # Generate list of years for filter dropdown
    available_years = Income.objects.annotate(year=TruncYear('date')).values_list('year', flat=True).distinct().order_by('-year')
    if not available_years:
         available_years = range(current_year, current_year - 5, -1)

    context = {
        "active_menu": "reports",
        "selected_year": year_param,
        "available_years": available_years,
        "contributions": contributions,
        "total_overall_contribution": total_overall_contribution, 
        "all_members": all_members, # Pass members for the filter dropdown
        "selected_member": member_param, # Pass selected member ID
        "selected_member_name": selected_member_instance.name if selected_member_instance else None, # Pass selected member name
    }
    return render(request, "reports/contribuicoes_anuais.html", context)

# --- Accountability Reports ---

@method_decorator(login_required, name="dispatch")
class AccountabilityReportListView(ListView):
    model = AccountabilityReport
    template_name = "reports/accountability_list.html"
    context_object_name = "reports"
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_menu"] = "reports"
        return context

@method_decorator(login_required, name="dispatch")
class AccountabilityReportDetailView(DetailView):
    model = AccountabilityReport
    template_name = "reports/accountability_detail.html"
    context_object_name = "report"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_menu"] = "reports"
        # Add documents to context
        context["documents"] = self.object.documents.all()
        return context

@method_decorator(login_required, name="dispatch")
class AccountabilityReportCreateView(CreateView):
    model = AccountabilityReport
    form_class = AccountabilityReportForm
    template_name = "reports/accountability_form.html"
    success_url = reverse_lazy("reports:accountability_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Nova Prestação de Contas"
        context["button_text"] = "Salvar Prestação"
        context["active_menu"] = "reports"
        if self.request.POST:
            context["document_formset"] = AccountabilityDocumentFormSet(self.request.POST, self.request.FILES, prefix="documents")
        else:
            context["document_formset"] = AccountabilityDocumentFormSet(prefix="documents")
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        document_formset = context["document_formset"]
        with transaction.atomic():
            self.object = form.save()
            if document_formset.is_valid():
                document_formset.instance = self.object
                document_formset.save()
                messages.success(self.request, "Prestação de contas criada com sucesso!")
                return super().form_valid(form)
            else:
                # If formset is invalid, render form again with errors
                return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Erro ao salvar a prestação de contas. Verifique os campos.")
        return super().form_invalid(form)

@method_decorator(login_required, name="dispatch")
class AccountabilityReportUpdateView(UpdateView):
    model = AccountabilityReport
    form_class = AccountabilityReportForm
    template_name = "reports/accountability_form.html"
    success_url = reverse_lazy("reports:accountability_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = f"Editar Prestação: {self.object.month:02d}/{self.object.year}"
        context["button_text"] = "Salvar Alterações"
        context["active_menu"] = "reports"
        if self.request.POST:
            context["document_formset"] = AccountabilityDocumentFormSet(self.request.POST, self.request.FILES, instance=self.object, prefix="documents")
        else:
            context["document_formset"] = AccountabilityDocumentFormSet(instance=self.object, prefix="documents")
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        document_formset = context["document_formset"]
        with transaction.atomic():
            self.object = form.save()
            if document_formset.is_valid():
                document_formset.instance = self.object
                document_formset.save()
                messages.success(self.request, "Prestação de contas atualizada com sucesso!")
                return super().form_valid(form)
            else:
                return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Erro ao atualizar a prestação de contas. Verifique os campos.")
        return super().form_invalid(form)

@method_decorator(login_required, name="dispatch")
class AccountabilityReportDeleteView(DeleteView):
    model = AccountabilityReport
    template_name = "reports/accountability_confirm_delete.html"
    success_url = reverse_lazy("reports:accountability_list")
    context_object_name = "report"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = f"Confirmar Exclusão: {self.object.month:02d}/{self.object.year}"
        context["active_menu"] = "reports"
        return context

    def form_valid(self, form):
        messages.success(self.request, f"Prestação de contas {self.object.month:02d}/{self.object.year} excluída com sucesso.")
        return super().form_valid(form)


from django.template.loader import render_to_string
from weasyprint import HTML

@login_required
def export_movimentacoes_mensais_pdf(request):
    filters = _get_report_filters(request)
    first_day_month = filters["filter_date"]
    last_day_month = first_day_month + relativedelta(months=1) - relativedelta(days=1)
    
    incomes = Income.objects.filter(date__gte=first_day_month, date__lte=last_day_month).order_by("date")
    expenses = Expense.objects.filter(date__gte=first_day_month, date__lte=last_day_month).order_by("date")

    total_incomes = sum(i.amount for i in incomes)
    total_expenses = sum(e.amount for e in expenses)
    month_balance = total_incomes - total_expenses

    context = {
        "incomes": incomes, 
        "expenses": expenses, 
        "total_incomes": total_incomes, 
        "total_expenses": total_expenses, 
        "month_balance": month_balance, 
        "selected_month": first_day_month.month, 
        "selected_year": first_day_month.year, 
        "month_name": first_day_month.strftime("%B"),
        "is_pdf_export": True, # Flag to adjust template rendering if needed
    }

    # Render HTML template to string
    html_string = render_to_string("reports/movimentacoes_mensais_pdf_template.html", context)

    # Generate PDF
    #pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()

    # Create HTTP response
    response = HttpResponse(None, content_type="application/pdf")
    response["Content-Disposition"] = f"attachment; filename=movimentacoes_{first_day_month.strftime('%Y_%m')}.pdf"
    return response




@login_required
def export_dre_pdf(request):
    filters = _get_report_filters(request)
    year_param = filters["year_param"]
    first_day_year = date(year_param, 1, 1)
    last_day_year = date(year_param, 12, 31)

    incomes_by_category = Income.objects.filter(
        date__gte=first_day_year, date__lte=last_day_year
    ).values("category__name").annotate(total=Sum("amount")).order_by("-total")

    expenses_by_category = Expense.objects.filter(
        date__gte=first_day_year, date__lte=last_day_year
    ).values("category__name").annotate(total=Sum("amount")).order_by("-total")

    total_revenue = sum(item["total"] for item in incomes_by_category) or 0
    total_expenditure = sum(item["total"] for item in expenses_by_category) or 0
    net_result = total_revenue - total_expenditure

    context = {
        "selected_year": year_param,
        "incomes_by_category": incomes_by_category, 
        "expenses_by_category": expenses_by_category, 
        "total_revenue": total_revenue, 
        "total_expenditure": total_expenditure, 
        "net_result": net_result, 
        "is_pdf_export": True,
    }

    html_string = render_to_string("reports/dre_pdf_template.html", context)
    #pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()

    response = HttpResponse(None, content_type="application/pdf")
    response["Content-Disposition"] = f"attachment; filename=dre_{year_param}.pdf"
    return response

@login_required
def export_dre_xlsx(request):
    filters = _get_report_filters(request)
    year_param = filters["year_param"]
    first_day_year = date(year_param, 1, 1)
    last_day_year = date(year_param, 12, 31)

    incomes_by_category = Income.objects.filter(
        date__gte=first_day_year, date__lte=last_day_year
    ).values("category__name").annotate(total=Sum("amount")).order_by("-total")

    expenses_by_category = Expense.objects.filter(
        date__gte=first_day_year, date__lte=last_day_year
    ).values("category__name").annotate(total=Sum("amount")).order_by("-total")

    total_revenue = sum(item["total"] for item in incomes_by_category) or 0
    total_expenditure = sum(item["total"] for item in expenses_by_category) or 0
    net_result = total_revenue - total_expenditure

    wb = Workbook()
    ws = wb.active
    ws.title = f"DRE {year_param}"

    # Title
    ws.merge_cells("A1:B1")
    title_cell = ws["A1"]
    title_cell.value = f"Demonstração do Resultado do Exercício - {year_param}"
    title_cell.font = Font(bold=True, size=14)
    title_cell.alignment = Alignment(horizontal="center")
    ws.row_dimensions[1].height = 20

    # Revenues Section
    ws.append([]) # Spacer row
    ws.append(["Receitas Operacionais"])
    ws["A3"].font = Font(bold=True, size=12)
    ws.append(["Categoria", "Valor"])
    header_font = Font(bold=True)
    ws["A4"].font = header_font
    ws["B4"].font = header_font

    row = 5
    for item in incomes_by_category:
        ws.append([
            item["category__name"] or "Sem Categoria",
            item["total"]
        ])
        ws[f"B{row}"].number_format = "R$ #,##0.00"
        row += 1

    ws.append(["Total Receitas:", total_revenue])
    ws[f"A{row}"].font = Font(bold=True)
    ws[f"B{row}"].font = Font(bold=True)
    ws[f"B{row}"].number_format = "R$ #,##0.00"
    row += 1

    # Expenses Section
    ws.append([]) # Spacer row
    row += 1
    ws.append(["Despesas Operacionais"])
    ws[f"A{row}"].font = Font(bold=True, size=12)
    row += 1
    ws.append(["Categoria", "Valor"])
    ws[f"A{row}"].font = header_font
    ws[f"B{row}"].font = header_font
    row += 1

    for item in expenses_by_category:
        ws.append([
            item["category__name"] or "Sem Categoria",
            item["total"]
        ])
        ws[f"B{row}"].number_format = "R$ #,##0.00"
        row += 1

    ws.append(["Total Despesas:", total_expenditure])
    ws[f"A{row}"].font = Font(bold=True)
    ws[f"B{row}"].font = Font(bold=True)
    ws[f"B{row}"].number_format = "R$ #,##0.00"
    row += 1

    # Net Result Section
    ws.append([]) # Spacer row
    row += 1
    ws.append(["Resultado Líquido:", net_result])
    ws[f"A{row}"].font = Font(bold=True, size=12)
    ws[f"B{row}"].font = Font(bold=True, size=12)
    ws[f"B{row}"].number_format = "R$ #,##0.00"

    # Adjust column widths
    ws.column_dimensions["A"].width = 35
    ws.column_dimensions["B"].width = 15

    # Save to buffer
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    response = HttpResponse(
        buffer,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f"attachment; filename=dre_{year_param}.xlsx"
    return response




@login_required
def export_balanco_pdf(request):
    filters = _get_report_filters(request)
    end_date = filters["end_date"]

    total_incomes_accumulated = Income.objects.filter(date__lte=end_date).aggregate(total=Sum("amount"))["total"] or 0
    total_expenses_accumulated = Expense.objects.filter(date__lte=end_date).aggregate(total=Sum("amount"))["total"] or 0
    accumulated_balance = total_incomes_accumulated - total_expenses_accumulated

    assets = {
        "Caixa/Banco (Saldo Acumulado)": accumulated_balance,
        # Add other asset accounts here if model supports
    }
    liabilities_equity = {
        "Patrimônio Líquido (Resultado Acumulado)": accumulated_balance, # Simplification
        # Add other liability/equity accounts here if model supports
    }
    total_assets = sum(assets.values())
    total_liabilities_equity = sum(liabilities_equity.values())

    context = {
        "end_date": end_date, 
        "assets": assets,
        "liabilities_equity": liabilities_equity, 
        "total_assets": total_assets,
        "total_liabilities_equity": total_liabilities_equity, 
        "is_pdf_export": True,
    }

    html_string = render_to_string("reports/balanco_pdf_template.html", context)
    #pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()

    response = HttpResponse(None, content_type="application/pdf")
    response["Content-Disposition"] = f"attachment; filename=balanco_{end_date.strftime('%Y%m%d')}.pdf"
    return response

@login_required
def export_balanco_xlsx(request):
    filters = _get_report_filters(request)
    end_date = filters["end_date"]

    total_incomes_accumulated = Income.objects.filter(date__lte=end_date).aggregate(total=Sum("amount"))["total"] or 0
    total_expenses_accumulated = Expense.objects.filter(date__lte=end_date).aggregate(total=Sum("amount"))["total"] or 0
    accumulated_balance = total_incomes_accumulated - total_expenses_accumulated

    assets = {
        "Caixa/Banco (Saldo Acumulado)": accumulated_balance,
    }
    liabilities_equity = {
        "Patrimônio Líquido (Resultado Acumulado)": accumulated_balance, # Simplification
    }
    total_assets = sum(assets.values())
    total_liabilities_equity = sum(liabilities_equity.values())

    wb = Workbook()
    ws = wb.active
    ws.title = f"Balanço {end_date.strftime('%d-%m-%Y')}"

    # Title
    ws.merge_cells("A1:B1")
    title_cell = ws["A1"]
    title_cell.value = f"Balanço Patrimonial Simplificado em {end_date.strftime('%d/%m/%Y')}"
    title_cell.font = Font(bold=True, size=14)
    title_cell.alignment = Alignment(horizontal="center")
    ws.row_dimensions[1].height = 20

    # Assets Section
    ws.append([]) # Spacer row
    ws.append(["Ativo"])
    ws["A3"].font = Font(bold=True, size=12)
    ws.append(["Conta", "Valor"])
    header_font = Font(bold=True)
    ws["A4"].font = header_font
    ws["B4"].font = header_font

    row = 5
    for account, value in assets.items():
        ws.append([account, value])
        ws[f"B{row}"].number_format = "R$ #,##0.00"
        row += 1

    ws.append(["Total Ativo:", total_assets])
    ws[f"A{row}"].font = Font(bold=True)
    ws[f"B{row}"].font = Font(bold=True)
    ws[f"B{row}"].number_format = "R$ #,##0.00"
    row += 1

    # Liabilities & Equity Section
    ws.append([]) # Spacer row
    row += 1
    ws.append(["Passivo e Patrimônio Líquido"])
    ws[f"A{row}"].font = Font(bold=True, size=12)
    row += 1
    ws.append(["Conta", "Valor"])
    ws[f"A{row}"].font = header_font
    ws[f"B{row}"].font = header_font
    row += 1

    for account, value in liabilities_equity.items():
        ws.append([account, value])
        ws[f"B{row}"].number_format = "R$ #,##0.00"
        row += 1

    ws.append(["Total Passivo e PL:", total_liabilities_equity])
    ws[f"A{row}"].font = Font(bold=True)
    ws[f"B{row}"].font = Font(bold=True)
    ws[f"B{row}"].number_format = "R$ #,##0.00"

    # Adjust column widths
    ws.column_dimensions["A"].width = 40
    ws.column_dimensions["B"].width = 15

    # Save to buffer
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    response = HttpResponse(
        buffer,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f"attachment; filename=balanco_{end_date.strftime('%Y%m%d')}.xlsx"
    return response




@login_required
def export_alunos_por_turma_pdf(request):
    classes = SchoolClass.objects.annotate(num_students=Count("students")).order_by("name")
    total_students = Student.objects.count()

    context = {
        "classes": classes, 
        "total_students": total_students,
        "is_pdf_export": True,
    }

    html_string = render_to_string("reports/alunos_por_turma_pdf_template.html", context)
    #pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()

    response = HttpResponse(None, content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=alunos_por_turma.pdf"
    return response

@login_required
def export_alunos_por_turma_xlsx(request):
    classes = SchoolClass.objects.annotate(num_students=Count("students")).order_by("name")
    total_students = Student.objects.count()

    wb = Workbook()
    ws = wb.active
    ws.title = "Alunos por Turma"

    # Title
    ws.merge_cells("A1:B1")
    title_cell = ws["A1"]
    title_cell.value = "Relatório de Alunos por Turma"
    title_cell.font = Font(bold=True, size=14)
    title_cell.alignment = Alignment(horizontal="center")
    ws.row_dimensions[1].height = 20

    # Header
    ws.append([]) # Spacer row
    ws.append(["Turma", "Nº de Alunos"])
    header_font = Font(bold=True)
    ws["A3"].font = header_font
    ws["B3"].font = header_font

    # Data
    row = 4
    for cls in classes:
        ws.append([
            cls.name,
            cls.num_students
        ])
        row += 1

    # Total
    ws.append([]) # Spacer row
    row += 1
    ws.append(["Total Geral de Alunos:", total_students])
    ws[f"A{row}"].font = Font(bold=True)
    ws[f"B{row}"].font = Font(bold=True)

    # Adjust column widths
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 15

    # Save to buffer
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    response = HttpResponse(
        buffer,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=alunos_por_turma.xlsx"
    return response




@login_required
def export_frequencia_pdf(request):
    filters = _get_report_filters(request)
    class_id = filters["class_id"]
    class_date = filters["class_date"]

    attendances = Attendance.objects.filter(date=class_date).select_related("student__member", "school_class")
    selected_class = None
    if class_id:
        try:
            selected_class = SchoolClass.objects.get(pk=class_id)
            attendances = attendances.filter(school_class_id=class_id)
        except SchoolClass.DoesNotExist:
            class_id = None

    attendances = attendances.order_by("school_class__name", "student__member__name")
    total_present = attendances.filter(present=True).count()
    total_absent = attendances.filter(present=False).count()
    total_records = attendances.count()

    context = {
        "selected_class_name": selected_class.name if selected_class else "Todas as Turmas",
        "class_date": class_date,
        "attendances": attendances,
        "total_present": total_present,
        "total_absent": total_absent,
        "total_records": total_records,
        "is_pdf_export": True,
    }

    html_string = render_to_string("reports/frequencia_pdf_template.html", context)
    #pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()

    response = HttpResponse(None, content_type="application/pdf")
    filename_suffix = f"_{selected_class.name.replace(' ', '_')}" if selected_class else "_todas"
    response["Content-Disposition"] = f"attachment; filename=frequencia_{class_date.strftime('%Y%m%d')}{filename_suffix}.pdf"
    return response

@login_required
def export_frequencia_xlsx(request):
    filters = _get_report_filters(request)
    class_id = filters["class_id"]
    class_date = filters["class_date"]

    attendances = Attendance.objects.filter(date=class_date).select_related("student__member", "school_class")
    selected_class = None
    if class_id:
        try:
            selected_class = SchoolClass.objects.get(pk=class_id)
            attendances = attendances.filter(school_class_id=class_id)
        except SchoolClass.DoesNotExist:
            class_id = None

    attendances = attendances.order_by("school_class__name", "student__member__name")
    total_present = attendances.filter(present=True).count()
    total_absent = attendances.filter(present=False).count()
    total_records = attendances.count()

    wb = Workbook()
    ws = wb.active
    ws.title = f"Frequência {class_date.strftime('%d-%m-%Y')}"

    # Title
    class_name_title = selected_class.name if selected_class else "Todas as Turmas"
    ws.merge_cells("A1:D1")
    title_cell = ws["A1"]
    title_cell.value = f"Relatório de Frequência - {class_name_title} - {class_date.strftime('%d/%m/%Y')}"
    title_cell.font = Font(bold=True, size=14)
    title_cell.alignment = Alignment(horizontal="center")
    ws.row_dimensions[1].height = 20

    # Header
    ws.append([]) # Spacer row
    ws.append(["Turma", "Aluno", "Presente", "Observação"])
    header_font = Font(bold=True)
    for col in ["A", "B", "C", "D"]:
        ws[f"{col}3"].font = header_font

    # Data
    row = 4
    for att in attendances:
        ws.append([
            att.school_class.name,
            att.student.member.name,
            "Sim" if att.present else "Não",
            att.observation
        ])
        row += 1

    # Summary
    ws.append([]) # Spacer row
    row += 1
    ws.append(["", "", "Total Presentes:", total_present])
    ws[f"C{row}"].font = Font(bold=True)
    ws[f"D{row}"].font = Font(bold=True)
    row += 1
    ws.append(["", "", "Total Ausentes:", total_absent])
    ws[f"C{row}"].font = Font(bold=True)
    ws[f"D{row}"].font = Font(bold=True)
    row += 1
    ws.append(["", "", "Total Registros:", total_records])
    ws[f"C{row}"].font = Font(bold=True)
    ws[f"D{row}"].font = Font(bold=True)

    # Adjust column widths
    ws.column_dimensions["A"].width = 25
    ws.column_dimensions["B"].width = 35
    ws.column_dimensions["C"].width = 15
    ws.column_dimensions["D"].width = 30

    # Save to buffer
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    response = HttpResponse(
        buffer,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    filename_suffix = f"_{selected_class.name.replace(' ', '_')}" if selected_class else "_todas"
    response["Content-Disposition"] = f"attachment; filename=frequencia_{class_date.strftime('%Y%m%d')}{filename_suffix}.xlsx"
    return response




@login_required
def export_membros_estatisticas_pdf(request):
    total_members = Member.objects.count()
    active_members = Member.objects.filter(status="active").count()
    members_by_status = Member.objects.values("status").annotate(count=Count("id")).order_by("-count")
    members_by_gender = Member.objects.values("gender").annotate(count=Count("id")).order_by("-count")
    members_by_marital_status = Member.objects.values("marital_status").annotate(count=Count("id")).order_by("-count")
    members_by_type = Member.objects.values("member_type").annotate(count=Count("id")).order_by("-count")

    status_map = dict(Member.STATUS_CHOICES)
    gender_map = dict(Member.GENDER_CHOICES)
    marital_map = dict(Member.MARITAL_STATUS_CHOICES)
    type_map = dict(Member.MEMBER_TYPE_CHOICES)

    context = {
        "total_members": total_members,
        "active_members": active_members, 
        "members_by_status": [(status_map.get(item["status"], item["status"]), item["count"]) for item in members_by_status],
        "members_by_gender": [(gender_map.get(item["gender"], item["gender"]), item["count"]) for item in members_by_gender],
        "members_by_marital_status": [(marital_map.get(item["marital_status"], item["marital_status"]), item["count"]) for item in members_by_marital_status],
        "members_by_type": [(type_map.get(item["member_type"], item["member_type"]), item["count"]) for item in members_by_type],
        "is_pdf_export": True,
    }

    html_string = render_to_string("reports/membros_estatisticas_pdf_template.html", context)
    #pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()

    response = HttpResponse(None, content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=membros_estatisticas.pdf"
    return response

@login_required
def export_membros_estatisticas_xlsx(request):
    total_members = Member.objects.count()
    active_members = Member.objects.filter(status="active").count()
    members_by_status = Member.objects.values("status").annotate(count=Count("id")).order_by("-count")
    members_by_gender = Member.objects.values("gender").annotate(count=Count("id")).order_by("-count")
    members_by_marital_status = Member.objects.values("marital_status").annotate(count=Count("id")).order_by("-count")
    members_by_type = Member.objects.values("member_type").annotate(count=Count("id")).order_by("-count")

    status_map = dict(Member.STATUS_CHOICES)
    gender_map = dict(Member.GENDER_CHOICES)
    marital_map = dict(Member.MARITAL_STATUS_CHOICES)
    type_map = dict(Member.MEMBER_TYPE_CHOICES)

    wb = Workbook()
    ws = wb.active
    ws.title = "Estatísticas de Membros"

    # Title
    ws.merge_cells("A1:B1")
    title_cell = ws["A1"]
    title_cell.value = "Relatório de Estatísticas de Membros"
    title_cell.font = Font(bold=True, size=14)
    title_cell.alignment = Alignment(horizontal="center")
    ws.row_dimensions[1].height = 20

    # Summary
    ws.append([])
    ws.append(["Total de Membros:", total_members])
    ws.append(["Membros Ativos:", active_members])
    ws["A3"].font = Font(bold=True)
    ws["A4"].font = Font(bold=True)
    ws["B3"].font = Font(bold=True)
    ws["B4"].font = Font(bold=True)

    header_font = Font(bold=True)
    row = 6

    # By Status
    ws.append([])
    row += 1
    ws.append(["Membros por Status"])
    ws[f"A{row}"].font = Font(bold=True, size=12)
    row += 1
    ws.append(["Status", "Quantidade"])
    ws[f"A{row}"].font = header_font
    ws[f"B{row}"].font = header_font
    row += 1
    for status, count in [(status_map.get(item["status"], item["status"]), item["count"]) for item in members_by_status]:
        ws.append([status, count])
        row += 1

    # By Gender
    ws.append([])
    row += 1
    ws.append(["Membros por Gênero"])
    ws[f"A{row}"].font = Font(bold=True, size=12)
    row += 1
    ws.append(["Gênero", "Quantidade"])
    ws[f"A{row}"].font = header_font
    ws[f"B{row}"].font = header_font
    row += 1
    for gender, count in [(gender_map.get(item["gender"], item["gender"]), item["count"]) for item in members_by_gender]:
        ws.append([gender, count])
        row += 1

    # By Marital Status
    ws.append([])
    row += 1
    ws.append(["Membros por Estado Civil"])
    ws[f"A{row}"].font = Font(bold=True, size=12)
    row += 1
    ws.append(["Estado Civil", "Quantidade"])
    ws[f"A{row}"].font = header_font
    ws[f"B{row}"].font = header_font
    row += 1
    for marital_status, count in [(marital_map.get(item["marital_status"], item["marital_status"]), item["count"]) for item in members_by_marital_status]:
        ws.append([marital_status, count])
        row += 1

    # By Type
    ws.append([])
    row += 1
    ws.append(["Membros por Tipo"])
    ws[f"A{row}"].font = Font(bold=True, size=12)
    row += 1
    ws.append(["Tipo", "Quantidade"])
    ws[f"A{row}"].font = header_font
    ws[f"B{row}"].font = header_font
    row += 1
    for member_type, count in [(type_map.get(item["member_type"], item["member_type"]), item["count"]) for item in members_by_type]:
        ws.append([member_type, count])
        row += 1

    # Adjust column widths
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 15

    # Save to buffer
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    response = HttpResponse(
        buffer,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=membros_estatisticas.xlsx"
    return response




@login_required
def relatorio_financeiro_categorias(request):
    filters = _get_report_filters(request)
    month_param = filters["month_param"]
    year_param = filters["year_param"]

    start_date = date(year_param, month_param, 1)
    end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)

    # Fetch incomes and group by category
    incomes = Income.objects.filter(date__gte=start_date, date__lte=end_date).select_related("category").order_by("category__name", "date")
    incomes_grouped = {}
    total_revenue = Decimal("0.00")
    for income in incomes:
        category_name = income.category.name if income.category else "Sem Categoria"
        if category_name not in incomes_grouped:
            incomes_grouped[category_name] = {"items": [], "total": Decimal("0.00")}
        incomes_grouped[category_name]["items"].append(income)
        incomes_grouped[category_name]["total"] += income.amount
        total_revenue += income.amount

    # Fetch expenses and group by category
    expenses = Expense.objects.filter(date__gte=start_date, date__lte=end_date).select_related("category").order_by("category__name", "date")
    expenses_grouped = {}
    total_expenditure = Decimal("0.00")
    for expense in expenses:
        category_name = expense.category.name if expense.category else "Sem Categoria"
        if category_name not in expenses_grouped:
            expenses_grouped[category_name] = {"items": [], "total": Decimal("0.00")}
        expenses_grouped[category_name]["items"].append(expense)
        expenses_grouped[category_name]["total"] += expense.amount
        total_expenditure += expense.amount

    # Calculate final balance
    final_balance = total_revenue - total_expenditure

    # Prepare context
    context = {
        "selected_month": month_param,
        "selected_year": year_param,
        "available_years": filters["available_years"],
        "available_months": filters["available_months"],
        "start_date": start_date,
        "end_date": end_date,
        "incomes_grouped": dict(sorted(incomes_grouped.items())),
        "expenses_grouped": dict(sorted(expenses_grouped.items())),
        "total_revenue": total_revenue,
        "total_expenditure": total_expenditure,
        "final_balance": final_balance,
        "filters_query_string": request.GET.urlencode(),
    }

    return render(request, "reports/financeiro_categorias.html", context)

