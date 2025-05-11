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
from core.models import ChurchConfiguration # Import ChurchConfiguration
from django.utils import timezone
from datetime import date, timedelta # Added timedelta
from decimal import Decimal # Added Decimal
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
from openpyxl.drawing.image import Image as OpenpyxlImage # For adding images to Excel
import io
from django.template.loader import render_to_string
#from weasyprint import HTML, CSS
from django.conf import settings # For MEDIA_ROOT
import os # For path joining


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
    
    # Get church configuration
    church_config = ChurchConfiguration.objects.first()

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
        "church_config": church_config,
        "available_years": range(current_year, current_year - 5, -1),
        "available_months": {
            1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
            5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
            9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
        }
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

    context = {
        "active_menu": "reports",
        "incomes": incomes, 
        "expenses": expenses, 
        "total_incomes": total_incomes, 
        "total_expenses": total_expenses, 
        "month_balance": month_balance, 
        "selected_month": first_day_month.month, 
        "selected_year": first_day_month.year, 
        "month_name": filters["available_months"].get(first_day_month.month),
        "available_years": filters["available_years"],
        "available_months": filters["available_months"],
        "filters_query_string": request.GET.urlencode(),
        "church_config": filters["church_config"],
    }
    return render(request, "reports/movimentacoes_mensais.html", context)


@login_required
def export_movimentacoes_mensais_xlsx(request):
    filters = _get_report_filters(request)
    church_config = filters["church_config"]
    first_day_month = filters["filter_date"]
    last_day_month = first_day_month + relativedelta(months=1) - relativedelta(days=1)

    incomes = Income.objects.filter(date__gte=first_day_month, date__lte=last_day_month).order_by("date")
    expenses = Expense.objects.filter(date__gte=first_day_month, date__lte=last_day_month).order_by("date")
    total_incomes = sum(i.amount for i in incomes)
    total_expenses = sum(e.amount for e in expenses)
    month_balance = total_incomes - total_expenses

    wb = Workbook()
    ws = wb.active
    ws.title = f"Mov. {first_day_month.strftime("%b_%Y")}"
    current_row = 1

    # Church Info Header
    if church_config:
        if church_config.logo and hasattr(church_config.logo, "path") and os.path.exists(church_config.logo.path):
            try:
                img = OpenpyxlImage(church_config.logo.path)
                img.height = 75 # Adjust as needed
                img.width = 75  # Adjust as needed
                ws.add_image(img, "A1")
            except Exception as e:
                print(f"Error adding logo to Excel: {e}") # Log error
        ws.merge_cells(start_row=current_row, start_column=2, end_row=current_row, end_column=5)
        cell = ws.cell(row=current_row, column=2, value=church_config.church_name or "Nome da Igreja")
        cell.font = Font(bold=True, size=16)
        cell.alignment = Alignment(horizontal="center")
        current_row += 1
        ws.merge_cells(start_row=current_row, start_column=2, end_row=current_row, end_column=5)
        cell = ws.cell(row=current_row, column=2, value=f"Pastor Presidente: {church_config.president_pastor_name or "-"} | Tesoureiro(a): {church_config.treasurer_name or "-"}")
        cell.font = Font(size=10)
        cell.alignment = Alignment(horizontal="center")
        current_row += 1

    # Report Title
    ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=5)
    title_cell = ws.cell(row=current_row, column=1, value=f"Relatório de Movimentações Mensais - {filters["available_months"].get(first_day_month.month)} {first_day_month.year}")
    title_cell.font = Font(bold=True, size=14)
    title_cell.alignment = Alignment(horizontal="center")
    ws.row_dimensions[current_row].height = 20
    current_row += 1
    
    ws.append([]) # Spacer row
    current_row +=1

    # Incomes Section
    ws.cell(row=current_row, column=1, value="Receitas").font = Font(bold=True, size=12)
    current_row += 1
    header_incomes = ["Data", "Descrição", "Categoria", "Membro", "Valor"]
    ws.append(header_incomes)
    header_font = Font(bold=True)
    for col_idx, _ in enumerate(header_incomes, 1):
        ws.cell(row=current_row, column=col_idx).font = header_font
    current_row += 1

    for income in incomes:
        ws.append([
            income.date,
            income.description,
            income.category.name if income.category else "",
            income.member.name if income.member else "",
            income.amount
        ])
        ws.cell(row=current_row, column=5).number_format = "R$ #,##0.00"
        current_row += 1

    ws.append(["", "", "", "Total Receitas:", total_incomes])
    ws.cell(row=current_row, column=4).font = Font(bold=True)
    ws.cell(row=current_row, column=5).font = Font(bold=True)
    ws.cell(row=current_row, column=5).number_format = "R$ #,##0.00"
    current_row += 1

    # Expenses Section
    ws.append([]) # Spacer row
    current_row +=1
    ws.cell(row=current_row, column=1, value="Despesas").font = Font(bold=True, size=12)
    current_row += 1
    header_expenses = ["Data", "Descrição", "Categoria", "", "Valor"]
    ws.append(header_expenses)
    for col_idx, _ in enumerate(header_expenses, 1):
        if ws.cell(row=current_row, column=col_idx).value: # Apply font only if cell has value
             ws.cell(row=current_row, column=col_idx).font = header_font
    current_row += 1

    for expense in expenses:
        ws.append([
            expense.date,
            expense.description,
            expense.category.name if expense.category else "",
            "",
            expense.amount
        ])
        ws.cell(row=current_row, column=5).number_format = "R$ #,##0.00"
        current_row += 1

    ws.append(["", "", "", "Total Despesas:", total_expenses])
    ws.cell(row=current_row, column=4).font = Font(bold=True)
    ws.cell(row=current_row, column=5).font = Font(bold=True)
    ws.cell(row=current_row, column=5).number_format = "R$ #,##0.00"
    current_row += 1

    # Balance Section
    ws.append([]) # Spacer row
    current_row += 1
    ws.append(["", "", "", "Saldo do Mês:", month_balance])
    ws.cell(row=current_row, column=4).font = Font(bold=True, size=12)
    ws.cell(row=current_row, column=5).font = Font(bold=True, size=12)
    ws.cell(row=current_row, column=5).number_format = "R$ #,##0.00"

    # Adjust column widths
    ws.column_dimensions["A"].width = 12
    ws.column_dimensions["B"].width = 35
    ws.column_dimensions["C"].width = 20
    ws.column_dimensions["D"].width = 20
    ws.column_dimensions["E"].width = 15

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    response = HttpResponse(
        buffer,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f"attachment; filename=movimentacoes_{first_day_month.strftime("%Y_%m")}.xlsx"
    return response

@login_required
def export_movimentacoes_mensais_pdf(request):
    filters = _get_report_filters(request)
    church_config = filters["church_config"]
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
        "report_period": f"{filters["available_months"].get(first_day_month.month)} {first_day_month.year}",
        "church_config": church_config,
    }
    html_string = render_to_string("reports/movimentacoes_mensais_pdf_template.html", context)
    
    # Add base_url for WeasyPrint to find static files like images if they are referenced in the template
    # This requires MEDIA_URL and MEDIA_ROOT to be set correctly in settings.py
    # and the image path in the template to be relative to MEDIA_ROOT or an absolute URL.
    # For local file paths, ensure they are absolute or construct them using settings.BASE_DIR or settings.MEDIA_ROOT.
    # Example: if church_config.logo.url is /media/church_logo/logo.png, then base_url should allow resolving it.
    # A common approach is to use request.build_absolute_uri("/") as base_url if your static/media are served by Django dev server
    # or configure static file serving properly for production.
    # For direct file paths from MEDIA_ROOT:
    base_url = settings.MEDIA_ROOT # This might not be directly usable by WeasyPrint for HTML relative paths.
                                  # It's often better to ensure template uses full URLs or data URIs for images in PDFs.
                                  # Or, pass the absolute path to the image in the context and use <img src="file:///path/to/image.png">
                                  # if WeasyPrint is configured to allow local file access.

    # For simplicity, if logo is stored and accessible via URL (e.g. /media/...), 
    # and your dev server serves media, WeasyPrint might find it if you pass request to template or use absolute URLs.
    # If logo path is local, you might need to embed it as base64 or ensure WeasyPrint can access it.
    # We'll assume the template handles displaying the logo, possibly using church_config.logo.url

    #html = HTML(string=html_string, base_url=request.build_absolute_uri("/")) # Helps resolve relative URLs for CSS/Images
    #pdf_file = html.write_pdf()

    response = HttpResponse(None, content_type="application/pdf")
    response["Content-Disposition"] = f"attachment; filename=movimentacoes_{first_day_month.strftime("%Y_%m")}.pdf"
    return response


@login_required
def relatorio_dre(request):
    """
    Generates a financial report for the specified year, displaying income and 
    expenses categorized and summarized. The report includes total revenue, 
    total expenditure, and net result for the year.

    This view retrieves the financial data for the entire year based on the 
    year parameter from the request filters. It calculates the total income 
    and expenses by category and prepares the context for rendering the 
    "dre.html" template.

    The report is accessible only to authenticated users.

    Args:
        request (HttpRequest): The HTTP request object containing user data 
        and query parameters for filtering.

    Returns:
        HttpResponse: A response object containing the rendered "dre.html" 
        template with the financial report context.
    """

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
        "active_menu": "reports",
        "selected_year": year_param,
        "incomes_by_category": incomes_by_category, 
        "expenses_by_category": expenses_by_category, 
        "total_revenue": total_revenue, 
        "total_expenditure": total_expenditure, 
        "net_result": net_result, 
        "available_years": filters["available_years"],
        "filters_query_string": request.GET.urlencode(),
        "church_config": filters["church_config"],
    }
    return render(request, "reports/dre.html", context)

@login_required
def export_dre_xlsx(request):
    filters = _get_report_filters(request)
    church_config = filters["church_config"]
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
    current_row = 1

    if church_config:
        if church_config.logo and hasattr(church_config.logo, "path") and os.path.exists(church_config.logo.path):
            try:
                img = OpenpyxlImage(church_config.logo.path)
                img.height = 75; img.width = 75
                ws.add_image(img, "A1")
            except Exception as e:
                print(f"Error adding logo to DRE Excel: {e}")
        ws.merge_cells(start_row=current_row, start_column=2, end_row=current_row, end_column=3)
        cell = ws.cell(row=current_row, column=2, value=church_config.church_name or "Nome da Igreja")
        cell.font = Font(bold=True, size=16); cell.alignment = Alignment(horizontal="center")
        current_row += 1
        ws.merge_cells(start_row=current_row, start_column=2, end_row=current_row, end_column=3)
        cell = ws.cell(row=current_row, column=2, value=f"Pastor: {church_config.president_pastor_name or "-"} | Tesoureiro: {church_config.treasurer_name or "-"}")
        cell.font = Font(size=10); cell.alignment = Alignment(horizontal="center")
        current_row += 1

    ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=3)
    title_cell = ws.cell(row=current_row, column=1, value=f"Demonstração do Resultado do Exercício - {year_param}")
    title_cell.font = Font(bold=True, size=14); title_cell.alignment = Alignment(horizontal="center")
    ws.row_dimensions[current_row].height = 20
    current_row += 2

    ws.cell(row=current_row, column=1, value="Receitas Operacionais").font = Font(bold=True, size=12)
    current_row += 1
    ws.append(["Categoria", "Valor (R$)"])
    ws.cell(row=current_row, column=1).font = Font(bold=True)
    ws.cell(row=current_row, column=2).font = Font(bold=True)
    current_row += 1
    for item in incomes_by_category:
        ws.append([item["category__name"] or "Outras Receitas", item["total"]])
        ws.cell(row=current_row, column=2).number_format = "R$ #,##0.00"
        current_row += 1
    ws.append(["Total Receitas Operacionais", total_revenue])
    ws.cell(row=current_row, column=1).font = Font(bold=True)
    ws.cell(row=current_row, column=2).font = Font(bold=True)
    ws.cell(row=current_row, column=2).number_format = "R$ #,##0.00"
    current_row += 2

    ws.cell(row=current_row, column=1, value="Despesas Operacionais").font = Font(bold=True, size=12)
    current_row += 1
    ws.append(["Categoria", "Valor (R$)"])
    ws.cell(row=current_row, column=1).font = Font(bold=True)
    ws.cell(row=current_row, column=2).font = Font(bold=True)
    current_row += 1
    for item in expenses_by_category:
        ws.append([item["category__name"] or "Outras Despesas", item["total"]])
        ws.cell(row=current_row, column=2).number_format = "R$ #,##0.00"
        current_row += 1
    ws.append(["Total Despesas Operacionais", total_expenditure])
    ws.cell(row=current_row, column=1).font = Font(bold=True)
    ws.cell(row=current_row, column=2).font = Font(bold=True)
    ws.cell(row=current_row, column=2).number_format = "R$ #,##0.00"
    current_row += 2

    ws.append(["Resultado Líquido do Exercício", net_result])
    ws.cell(row=current_row, column=1).font = Font(bold=True, size=12)
    ws.cell(row=current_row, column=2).font = Font(bold=True, size=12)
    ws.cell(row=current_row, column=2).number_format = "R$ #,##0.00"

    ws.column_dimensions["A"].width = 35
    ws.column_dimensions["B"].width = 20
    ws.column_dimensions["C"].width = 20 # For merged church info

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f"attachment; filename=DRE_{year_param}.xlsx"
    return response

@login_required
def export_dre_pdf(request):
    filters = _get_report_filters(request)
    church_config = filters["church_config"]
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
        "report_period": str(year_param),
        "incomes_by_category": incomes_by_category,
        "expenses_by_category": expenses_by_category,
        "total_revenue": total_revenue,
        "total_expenditure": total_expenditure,
        "net_result": net_result,
        "church_config": church_config,
    }
    html_string = render_to_string("reports/dre_pdf_template.html", context)
    #html = HTML(string=html_string, base_url=request.build_absolute_uri("/"))
    #pdf_file = html.write_pdf()
    response = HttpResponse(None, content_type="application/pdf")
    response["Content-Disposition"] = f"attachment; filename=DRE_{year_param}.pdf"
    return response


@login_required
def relatorio_balanco(request):
    filters = _get_report_filters(request)
    end_date = filters["end_date"]
    total_incomes_accumulated = Income.objects.filter(date__lte=end_date).aggregate(total=Sum("amount"))["total"] or 0
    total_expenses_accumulated = Expense.objects.filter(date__lte=end_date).aggregate(total=Sum("amount"))["total"] or 0
    accumulated_balance = total_incomes_accumulated - total_expenses_accumulated
    assets = {"Caixa/Banco (Saldo Acumulado)": accumulated_balance}
    liabilities_equity = {"Patrimônio Líquido (Resultado Acumulado)": accumulated_balance}

    context = {
        "active_menu": "reports",
        "end_date": end_date, 
        "end_date_str": filters["end_date_str"],
        "assets": assets,
        "liabilities_equity": liabilities_equity, 
        "total_assets": sum(assets.values()),
        "total_liabilities_equity": sum(liabilities_equity.values()), 
        "filters_query_string": request.GET.urlencode(),
        "church_config": filters["church_config"],
    }
    return render(request, "reports/balanco.html", context)

@login_required
def export_balanco_xlsx(request):
    filters = _get_report_filters(request)
    church_config = filters["church_config"]
    end_date = filters["end_date"]
    total_incomes_accumulated = Income.objects.filter(date__lte=end_date).aggregate(total=Sum("amount"))["total"] or 0
    total_expenses_accumulated = Expense.objects.filter(date__lte=end_date).aggregate(total=Sum("amount"))["total"] or 0
    accumulated_balance = total_incomes_accumulated - total_expenses_accumulated
    assets = {"Caixa/Banco (Saldo Acumulado)": accumulated_balance}
    liabilities_equity = {"Patrimônio Líquido (Resultado Acumulado)": accumulated_balance}
    total_assets_val = sum(assets.values())
    total_liabilities_equity_val = sum(liabilities_equity.values())

    wb = Workbook()
    ws = wb.active
    ws.title = f"Balanco {end_date.strftime("%Y%m%d")}"
    current_row = 1

    if church_config:
        if church_config.logo and hasattr(church_config.logo, "path") and os.path.exists(church_config.logo.path):
            try:
                img = OpenpyxlImage(church_config.logo.path)
                img.height = 75; img.width = 75
                ws.add_image(img, "A1")
            except Exception as e:
                print(f"Error adding logo to Balanço Excel: {e}")
        ws.merge_cells(start_row=current_row, start_column=2, end_row=current_row, end_column=3)
        cell = ws.cell(row=current_row, column=2, value=church_config.church_name or "Nome da Igreja")
        cell.font = Font(bold=True, size=16); cell.alignment = Alignment(horizontal="center")
        current_row += 1
        ws.merge_cells(start_row=current_row, start_column=2, end_row=current_row, end_column=3)
        cell = ws.cell(row=current_row, column=2, value=f"Pastor: {church_config.president_pastor_name or "-"} | Tesoureiro: {church_config.treasurer_name or "-"}")
        cell.font = Font(size=10); cell.alignment = Alignment(horizontal="center")
        current_row += 1

    ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=3)
    title_cell = ws.cell(row=current_row, column=1, value=f"Balanço Patrimonial Simplificado - {end_date.strftime("%d/%m/%Y")}")
    title_cell.font = Font(bold=True, size=14); title_cell.alignment = Alignment(horizontal="center")
    ws.row_dimensions[current_row].height = 20
    current_row += 2

    ws.cell(row=current_row, column=1, value="Ativos").font = Font(bold=True, size=12)
    current_row += 1
    ws.append(["Conta", "Valor (R$)"])
    ws.cell(row=current_row, column=1).font = Font(bold=True)
    ws.cell(row=current_row, column=2).font = Font(bold=True)
    current_row += 1
    for conta, valor in assets.items():
        ws.append([conta, valor])
        ws.cell(row=current_row, column=2).number_format = "R$ #,##0.00"
        current_row += 1
    ws.append(["Total Ativos", total_assets_val])
    ws.cell(row=current_row, column=1).font = Font(bold=True)
    ws.cell(row=current_row, column=2).font = Font(bold=True)
    ws.cell(row=current_row, column=2).number_format = "R$ #,##0.00"
    current_row += 2

    ws.cell(row=current_row, column=1, value="Passivos e Patrimônio Líquido").font = Font(bold=True, size=12)
    current_row += 1
    ws.append(["Conta", "Valor (R$)"])
    ws.cell(row=current_row, column=1).font = Font(bold=True)
    ws.cell(row=current_row, column=2).font = Font(bold=True)
    current_row += 1
    for conta, valor in liabilities_equity.items():
        ws.append([conta, valor])
        ws.cell(row=current_row, column=2).number_format = "R$ #,##0.00"
        current_row += 1
    ws.append(["Total Passivos e Patrimônio Líquido", total_liabilities_equity_val])
    ws.cell(row=current_row, column=1).font = Font(bold=True)
    ws.cell(row=current_row, column=2).font = Font(bold=True)
    ws.cell(row=current_row, column=2).number_format = "R$ #,##0.00"

    ws.column_dimensions["A"].width = 40
    ws.column_dimensions["B"].width = 20
    ws.column_dimensions["C"].width = 20 # For merged church info

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f"attachment; filename=Balanco_{end_date.strftime("%Y%m%d")}.xlsx"
    return response

@login_required
def export_balanco_pdf(request):
    filters = _get_report_filters(request)
    church_config = filters["church_config"]
    end_date = filters["end_date"]
    total_incomes_accumulated = Income.objects.filter(date__lte=end_date).aggregate(total=Sum("amount"))["total"] or 0
    total_expenses_accumulated = Expense.objects.filter(date__lte=end_date).aggregate(total=Sum("amount"))["total"] or 0
    accumulated_balance = total_incomes_accumulated - total_expenses_accumulated
    assets = {"Caixa/Banco (Saldo Acumulado)": accumulated_balance}
    liabilities_equity = {"Patrimônio Líquido (Resultado Acumulado)": accumulated_balance}

    context = {
        "report_period": end_date.strftime("%d/%m/%Y"),
        "assets": assets,
        "liabilities_equity": liabilities_equity,
        "total_assets": sum(assets.values()),
        "total_liabilities_equity": sum(liabilities_equity.values()),
        "church_config": church_config,
    }
    html_string = render_to_string("reports/balanco_pdf_template.html", context)
    #html = HTML(string=html_string, base_url=request.build_absolute_uri("/"))
    #pdf_file = html.write_pdf()
    response = HttpResponse(None, content_type="application/pdf")
    response["Content-Disposition"] = f"attachment; filename=Balanco_{end_date.strftime("%Y%m%d")}.pdf"
    return response

# --- Relatórios da Escola Dominical ---
@login_required
def relatorio_alunos_por_turma(request):
    filters = _get_report_filters(request)
    classes = SchoolClass.objects.annotate(num_students=Count("students")).order_by("name")
    total_students = Student.objects.count()
    context = {
        "active_menu": "reports",
        "classes": classes, 
        "total_students": total_students,
        "church_config": filters["church_config"],
    }
    return render(request, "reports/alunos_por_turma.html", context)

@login_required
def export_alunos_por_turma_xlsx(request):
    filters = _get_report_filters(request)
    church_config = filters["church_config"]
    classes = SchoolClass.objects.annotate(num_students=Count("students")).order_by("name")
    total_students = Student.objects.count()

    wb = Workbook()
    ws = wb.active
    ws.title = "Alunos por Turma"
    current_row = 1

    if church_config:
        if church_config.logo and hasattr(church_config.logo, "path") and os.path.exists(church_config.logo.path):
            try:
                img = OpenpyxlImage(church_config.logo.path)
                img.height = 75; img.width = 75
                ws.add_image(img, "A1")
            except Exception as e:
                print(f"Error adding logo to Alunos Turma Excel: {e}")
        ws.merge_cells(start_row=current_row, start_column=2, end_row=current_row, end_column=3)
        cell = ws.cell(row=current_row, column=2, value=church_config.church_name or "Nome da Igreja")
        cell.font = Font(bold=True, size=16); cell.alignment = Alignment(horizontal="center")
        current_row += 1
        ws.merge_cells(start_row=current_row, start_column=2, end_row=current_row, end_column=3)
        cell = ws.cell(row=current_row, column=2, value=f"Pastor: {church_config.president_pastor_name or "-"} | Tesoureiro: {church_config.treasurer_name or "-"}")
        cell.font = Font(size=10); cell.alignment = Alignment(horizontal="center")
        current_row += 1

    ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=3)
    title_cell = ws.cell(row=current_row, column=1, value="Relatório de Alunos por Turma")
    title_cell.font = Font(bold=True, size=14); title_cell.alignment = Alignment(horizontal="center")
    ws.row_dimensions[current_row].height = 20
    current_row += 2

    ws.append(["Turma", "Nº de Alunos"])
    ws.cell(row=current_row, column=1).font = Font(bold=True)
    ws.cell(row=current_row, column=2).font = Font(bold=True)
    current_row += 1
    for c in classes:
        ws.append([c.name, c.num_students])
        current_row += 1
    ws.append(["Total Geral de Alunos", total_students])
    ws.cell(row=current_row, column=1).font = Font(bold=True)
    ws.cell(row=current_row, column=2).font = Font(bold=True)

    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 15
    ws.column_dimensions["C"].width = 20 # For merged church info

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = "attachment; filename=alunos_por_turma.xlsx"
    return response

@login_required
def export_alunos_por_turma_pdf(request):
    filters = _get_report_filters(request)
    church_config = filters["church_config"]
    classes = SchoolClass.objects.annotate(num_students=Count("students")).order_by("name")
    total_students = Student.objects.count()
    context = {
        "classes": classes,
        "total_students": total_students,
        "church_config": church_config,
        "report_period": "Geral" # Or specific if filtered
    }
    html_string = render_to_string("reports/alunos_por_turma_pdf_template.html", context)
    #html = HTML(string=html_string, base_url=request.build_absolute_uri("/"))
    #pdf_file = html.write_pdf()
    response = HttpResponse(None, content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=alunos_por_turma.pdf"
    return response


@login_required
def relatorio_frequencia(request):
    filters = _get_report_filters(request)
    class_id = filters["class_id"]
    class_date = filters["class_date"]
    classes = SchoolClass.objects.all().order_by("name")
    attendances = Attendance.objects.filter(date=class_date).select_related("student__member", "school_class")
    selected_class = None
    if class_id:
        try:
            selected_class = SchoolClass.objects.get(pk=class_id)
            attendances = attendances.filter(school_class_id=class_id)
        except SchoolClass.DoesNotExist:
            class_id = None # Reset if class not found

    attendances = attendances.order_by("school_class__name", "student__member__name")
    total_present = attendances.filter(present=True).count()
    total_absent = attendances.filter(present=False).count()
    total_records = attendances.count()

    context = {
        "active_menu": "reports",
        "classes": classes,
        "selected_class_id": class_id,
        "selected_class_name": selected_class.name if selected_class else "Todas as Turmas",
        "class_date": class_date,
        "class_date_str": filters["class_date_str"],
        "attendances": attendances,
        "total_present": total_present,
        "total_absent": total_absent,
        "total_records": total_records,
        "filters_query_string": request.GET.urlencode(),
        "church_config": filters["church_config"],
    }
    return render(request, "reports/frequencia.html", context)

@login_required
def export_frequencia_xlsx(request):
    filters = _get_report_filters(request)
    church_config = filters["church_config"]
    class_id = filters["class_id"]
    class_date = filters["class_date"]
    attendances = Attendance.objects.filter(date=class_date).select_related("student__member", "school_class")
    selected_class_name = "Todas as Turmas"
    if class_id:
        try:
            selected_class = SchoolClass.objects.get(pk=class_id)
            attendances = attendances.filter(school_class_id=class_id)
            selected_class_name = selected_class.name
        except SchoolClass.DoesNotExist:
            pass
    attendances = attendances.order_by("school_class__name", "student__member__name")
    total_present = attendances.filter(present=True).count()
    total_absent = attendances.filter(present=False).count()

    wb = Workbook()
    ws = wb.active
    ws.title = f"Frequencia {class_date.strftime("%Y%m%d")}"
    current_row = 1

    if church_config:
        if church_config.logo and hasattr(church_config.logo, "path") and os.path.exists(church_config.logo.path):
            try:
                img = OpenpyxlImage(church_config.logo.path)
                img.height = 75; img.width = 75
                ws.add_image(img, "A1")
            except Exception as e:
                print(f"Error adding logo to Frequencia Excel: {e}")
        ws.merge_cells(start_row=current_row, start_column=2, end_row=current_row, end_column=4)
        cell = ws.cell(row=current_row, column=2, value=church_config.church_name or "Nome da Igreja")
        cell.font = Font(bold=True, size=16); cell.alignment = Alignment(horizontal="center")
        current_row += 1
        ws.merge_cells(start_row=current_row, start_column=2, end_row=current_row, end_column=4)
        cell = ws.cell(row=current_row, column=2, value=f"Pastor: {church_config.president_pastor_name or "-"} | Tesoureiro: {church_config.treasurer_name or "-"}")
        cell.font = Font(size=10); cell.alignment = Alignment(horizontal="center")
        current_row += 1

    ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=4)
    title_cell = ws.cell(row=current_row, column=1, value=f"Relatório de Frequência - Turma: {selected_class_name} - Data: {class_date.strftime("%d/%m/%Y")}")
    title_cell.font = Font(bold=True, size=14); title_cell.alignment = Alignment(horizontal="center")
    ws.row_dimensions[current_row].height = 20
    current_row += 2

    ws.append(["Turma", "Aluno", "Status", "Observação"])
    header_font = Font(bold=True)
    for col_idx in range(1,5):
        ws.cell(row=current_row, column=col_idx).font = header_font
    current_row += 1

    for att in attendances:
        ws.append([
            att.school_class.name,
            att.student.member.name,
            "Presente" if att.present else "Ausente",
            att.observation
        ])
        current_row += 1
    
    current_row += 1
    ws.append(["", "Total Presentes:", total_present])
    ws.cell(row=current_row, column=2).font = Font(bold=True)
    current_row += 1
    ws.append(["", "Total Ausentes:", total_absent])
    ws.cell(row=current_row, column=2).font = Font(bold=True)

    ws.column_dimensions["A"].width = 25
    ws.column_dimensions["B"].width = 30
    ws.column_dimensions["C"].width = 12
    ws.column_dimensions["D"].width = 30

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f"attachment; filename=frequencia_{class_date.strftime("%Y%m%d")}.xlsx"
    return response

@login_required
def export_frequencia_pdf(request):
    filters = _get_report_filters(request)
    church_config = filters["church_config"]
    class_id = filters["class_id"]
    class_date = filters["class_date"]
    attendances = Attendance.objects.filter(date=class_date).select_related("student__member", "school_class")
    selected_class_name = "Todas as Turmas"
    if class_id:
        try:
            selected_class = SchoolClass.objects.get(pk=class_id)
            attendances = attendances.filter(school_class_id=class_id)
            selected_class_name = selected_class.name
        except SchoolClass.DoesNotExist:
            pass
    attendances = attendances.order_by("school_class__name", "student__member__name")
    total_present = attendances.filter(present=True).count()
    total_absent = attendances.filter(present=False).count()

    context = {
        "attendances": attendances,
        "report_period": f"Turma: {selected_class_name} - Data: {class_date.strftime("%d/%m/%Y")}",
        "total_present": total_present,
        "total_absent": total_absent,
        "church_config": church_config,
    }
    html_string = render_to_string("reports/frequencia_pdf_template.html", context)
    #html = HTML(string=html_string, base_url=request.build_absolute_uri("/"))
    #pdf_file = html.write_pdf()
    response = HttpResponse(None, content_type="application/pdf")
    response["Content-Disposition"] = f"attachment; filename=frequencia_{class_date.strftime("%Y%m%d")}.pdf"
    return response

# --- Relatórios de Membros ---
@login_required
def relatorio_membros_estatisticas(request):
    filters = _get_report_filters(request)
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
        "active_menu": "reports",
        "total_members": total_members,
        "active_members": active_members, 
        "members_by_status": [(status_map.get(item["status"], item["status"]), item["count"]) for item in members_by_status],
        "members_by_gender": [(gender_map.get(item["gender"], item["gender"]), item["count"]) for item in members_by_gender],
        "members_by_marital_status": [(marital_map.get(item["marital_status"], item["marital_status"]), item["count"]) for item in members_by_marital_status],
        "members_by_type": [(type_map.get(item["member_type"], item["member_type"]), item["count"]) for item in members_by_type],
        "church_config": filters["church_config"],
    }
    return render(request, "reports/members_estatisticas.html", context)

@login_required
def export_membros_estatisticas_xlsx(request):
    filters = _get_report_filters(request)
    church_config = filters["church_config"]
    total_members = Member.objects.count()
    active_members = Member.objects.filter(status="active").count()
    members_by_status = Member.objects.values("status").annotate(count=Count("id")).order_by("-count")
    members_by_gender = Member.objects.values("gender").annotate(count=Count("id")).order_by("-count")
    members_by_marital_status = Member.objects.values("marital_status").annotate(count=Count("id")).order_by("-count")
    members_by_type = Member.objects.values("member_type").annotate(count=Count("id")).order_by("-count")
    status_map = dict(Member.STATUS_CHOICES); gender_map = dict(Member.GENDER_CHOICES)
    marital_map = dict(Member.MARITAL_STATUS_CHOICES); type_map = dict(Member.MEMBER_TYPE_CHOICES)

    wb = Workbook()
    ws = wb.active
    ws.title = "Estatisticas Membros"
    current_row = 1

    if church_config:
        if church_config.logo and hasattr(church_config.logo, "path") and os.path.exists(church_config.logo.path):
            try:
                img = OpenpyxlImage(church_config.logo.path)
                img.height = 75; img.width = 75
                ws.add_image(img, "A1")
            except Exception as e:
                print(f"Error adding logo to Estatisticas Excel: {e}")
        ws.merge_cells(start_row=current_row, start_column=2, end_row=current_row, end_column=4) # Increased colspan for longer text
        cell = ws.cell(row=current_row, column=2, value=church_config.church_name or "Nome da Igreja")
        cell.font = Font(bold=True, size=16); cell.alignment = Alignment(horizontal="center")
        current_row += 1
        ws.merge_cells(start_row=current_row, start_column=2, end_row=current_row, end_column=4)
        cell = ws.cell(row=current_row, column=2, value=f"Pastor: {church_config.president_pastor_name or "-"} | Tesoureiro: {church_config.treasurer_name or "-"}")
        cell.font = Font(size=10); cell.alignment = Alignment(horizontal="center")
        current_row += 1

    ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=4)
    title_cell = ws.cell(row=current_row, column=1, value="Relatório de Estatísticas de Membros")
    title_cell.font = Font(bold=True, size=14); title_cell.alignment = Alignment(horizontal="center")
    ws.row_dimensions[current_row].height = 20
    current_row += 2

    ws.append(["Total de Membros:", total_members])
    ws.cell(row=current_row, column=1).font = Font(bold=True)
    current_row += 1
    ws.append(["Membros Ativos:", active_members])
    ws.cell(row=current_row, column=1).font = Font(bold=True)
    current_row += 2

    def add_stat_section(title, data_list, key_map):
        nonlocal current_row
        ws.cell(row=current_row, column=1, value=title).font = Font(bold=True, size=12)
        current_row += 1
        ws.append(["Item", "Quantidade"])
        ws.cell(row=current_row, column=1).font = Font(bold=True)
        ws.cell(row=current_row, column=2).font = Font(bold=True)
        current_row += 1
        for item_code, count in data_list:
            ws.append([key_map.get(item_code, item_code), count])
            current_row += 1
        current_row += 1 # Spacer

    add_stat_section("Por Status", [(item["status"], item["count"]) for item in members_by_status], status_map)
    add_stat_section("Por Gênero", [(item["gender"], item["count"]) for item in members_by_gender], gender_map)
    add_stat_section("Por Estado Civil", [(item["marital_status"], item["count"]) for item in members_by_marital_status], marital_map)
    add_stat_section("Por Tipo", [(item["member_type"], item["count"]) for item in members_by_type], type_map)

    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 15
    ws.column_dimensions["C"].width = 15 # For merged church info
    ws.column_dimensions["D"].width = 15 # For merged church info

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = "attachment; filename=membros_estatisticas.xlsx"
    return response

@login_required
def export_membros_estatisticas_pdf(request):
    filters = _get_report_filters(request)
    church_config = filters["church_config"]
    total_members = Member.objects.count()
    active_members = Member.objects.filter(status="active").count()
    members_by_status = Member.objects.values("status").annotate(count=Count("id")).order_by("-count")
    members_by_gender = Member.objects.values("gender").annotate(count=Count("id")).order_by("-count")
    members_by_marital_status = Member.objects.values("marital_status").annotate(count=Count("id")).order_by("-count")
    members_by_type = Member.objects.values("member_type").annotate(count=Count("id")).order_by("-count")
    status_map = dict(Member.STATUS_CHOICES); gender_map = dict(Member.GENDER_CHOICES)
    marital_map = dict(Member.MARITAL_STATUS_CHOICES); type_map = dict(Member.MEMBER_TYPE_CHOICES)

    context = {
        "total_members": total_members,
        "active_members": active_members,
        "members_by_status": [(status_map.get(item["status"], item["status"]), item["count"]) for item in members_by_status],
        "members_by_gender": [(gender_map.get(item["gender"], item["gender"]), item["count"]) for item in members_by_gender],
        "members_by_marital_status": [(marital_map.get(item["marital_status"], item["marital_status"]), item["count"]) for item in members_by_marital_status],
        "members_by_type": [(type_map.get(item["member_type"], item["member_type"]), item["count"]) for item in members_by_type],
        "church_config": church_config,
        "report_period": "Geral"
    }
    html_string = render_to_string("reports/membros_estatisticas_pdf_template.html", context)
    #html = HTML(string=html_string, base_url=request.build_absolute_uri("/"))
    #pdf_file = html.write_pdf()
    response = HttpResponse(None, content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=membros_estatisticas.pdf"
    return response

@login_required
def relatorio_aniversariantes(request):
    filters = _get_report_filters(request)
    month_param = filters["month_param"]
    birthdays = Member.objects.filter(birth_date__month=month_param)\
                                    .annotate(day=ExtractDay("birth_date"))\
                                    .order_by("day", "name")
    month_name = filters["available_months"].get(month_param, "")

    context = {
        "active_menu": "reports",
        "birthdays": birthdays, 
        "selected_month": month_param,
        "month_name": month_name,
        "available_months": filters["available_months"],
        "church_config": filters["church_config"],
    }
    return render(request, "reports/aniversariantes.html", context)

@login_required
def relatorio_contribuicoes_anuais(request):
    filters = _get_report_filters(request)
    year_param = filters["year_param"]
    member_param = filters["member_param"]
    all_members = Member.objects.filter(status="ativo").order_by("name")
    contributions_data = []
    selected_member_name = "Todos"

    if member_param and member_param != "all":
        members_to_query = Member.objects.filter(pk=member_param)
        if members_to_query.exists():
            selected_member_name = members_to_query.first().name
    else:
        members_to_query = all_members # All active members if "all" or no specific member
        member_param = "all" # Ensure it's set for template logic

    print(f"Member Param: {member_param}, Members to Query: {members_to_query}")

    for member_obj in members_to_query:
        monthly_contributions = []
        total_annual = Decimal("0.00")
        for month_num in range(1, 13):
            start_of_month = date(year_param, month_num, 1)
            end_of_month = (start_of_month + relativedelta(months=1)) - relativedelta(days=1)
            month_sum = Income.objects.filter(
                member=member_obj,
                date__gte=start_of_month,
                date__lte=end_of_month,
                category__name__iexact="Dízimo"  # Assuming category name for tithe
            ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
            monthly_contributions.append(month_sum)
            total_annual += month_sum
        contributions_data.append({
            "member_name": member_obj.name,
            "monthly_values": monthly_contributions,
            "total_annual": total_annual
        })
    
    total_overall_contribution = sum([item["total_annual"] for item in contributions_data])
    

    context = {
        "active_menu": "reports",
        "selected_year": year_param,
        "selected_member_id": member_param if member_param != "all" else "",
        "selected_member_name": selected_member_name,
        "all_members_for_filter": all_members,
        "contributions": contributions_data,
        "available_years": filters["available_years"],
        "months_header": [m[1][:3] for m in filters["available_months"].items()], # Jan, Fev, Mar...
        "church_config": filters["church_config"],
        "total_overall_contribution": total_overall_contribution,
        "grand_total_annual": sum([item["total_annual"] for item in contributions_data]), # VERIFICAR
    }
    return render(request, "reports/contribuicoes_anuais.html", context)


# Accountability Reports Views (Prestação de Contas)
@method_decorator(login_required, name='dispatch')
class AccountabilityReportListView(ListView):
    model = AccountabilityReport
    template_name = "reports/accountability_list.html"
    context_object_name = "reports"
    paginate_by = 10

    def get_queryset(self):
        return AccountabilityReport.objects.order_by("-year", "-month")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_menu"] = "reports"
        context["church_config"] = ChurchConfiguration.objects.first()
        return context

@method_decorator(login_required, name='dispatch')
class AccountabilityReportDetailView(DetailView):
    model = AccountabilityReport
    template_name = "reports/accountability_detail.html"
    context_object_name = "report"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_menu"] = "reports"
        context["church_config"] = ChurchConfiguration.objects.first()
        return context

@method_decorator(login_required, name='dispatch')
class AccountabilityReportCreateView(CreateView):
    model = AccountabilityReport
    form_class = AccountabilityReportForm
    template_name = "reports/accountability_form.html"
    success_url = reverse_lazy("reports:accountability_list")

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["documents_formset"] = AccountabilityDocumentFormSet(self.request.POST, self.request.FILES, prefix="documents")
        else:
            data["documents_formset"] = AccountabilityDocumentFormSet(prefix="documents")
        data["active_menu"] = "reports"
        data["church_config"] = ChurchConfiguration.objects.first()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        documents_formset = context["documents_formset"]
        with transaction.atomic():
            self.object = form.save()
            if documents_formset.is_valid():
                documents_formset.instance = self.object
                documents_formset.save()
            else:
                # If formset is invalid, re-render the form with errors
                # but first, ensure the main form object is not committed if transaction fails
                # However, CreateView typically saves before formset validation here.
                # Consider validating formset first or handling potential rollback.
                messages.error(self.request, "Erro nos documentos anexados.")
                return self.form_invalid(form) # This will re-render with formset errors
        messages.success(self.request, "Relatório de prestação de contas criado com sucesso!")
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class AccountabilityReportUpdateView(UpdateView):
    model = AccountabilityReport
    form_class = AccountabilityReportForm
    template_name = "reports/accountability_form.html"
    success_url = reverse_lazy("reports:accountability_list")

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["documents_formset"] = AccountabilityDocumentFormSet(self.request.POST, self.request.FILES, instance=self.object, prefix="documents")
        else:
            data["documents_formset"] = AccountabilityDocumentFormSet(instance=self.object, prefix="documents")
        data["active_menu"] = "reports"
        data["church_config"] = ChurchConfiguration.objects.first()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        documents_formset = context["documents_formset"]
        with transaction.atomic():
            self.object = form.save()
            if documents_formset.is_valid():
                documents_formset.save()
            else:
                messages.error(self.request, "Erro ao atualizar os documentos anexados.")
                return self.form_invalid(form)
        messages.success(self.request, "Relatório atualizado com sucesso!")
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class AccountabilityReportDeleteView(DeleteView):
    model = AccountabilityReport
    template_name = "reports/accountability_confirm_delete.html"
    success_url = reverse_lazy("reports:accountability_list")
    context_object_name = "report"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_menu"] = "reports"
        context["church_config"] = ChurchConfiguration.objects.first()
        return context

    def form_valid(self, form):
        messages.success(self.request, "Relatório de prestação de contas excluído com sucesso!")
        return super().form_valid(form)


@login_required
def relatorio_financeiro_categorias(request):
    filters = _get_report_filters(request)
    month_param = filters["month_param"]
    year_param = filters["year_param"]

    start_date = date(year_param, month_param, 1)
    end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)

    incomes = Income.objects.filter(date__gte=start_date, date__lte=end_date).select_related("category").order_by("category__name", "date")
    incomes_grouped = {}
    total_revenue = Decimal("0.00")
    for income_item in incomes: # Renamed to avoid conflict
        category_name = income_item.category.name if income_item.category else "Sem Categoria"
        if category_name not in incomes_grouped:
            incomes_grouped[category_name] = {"items": [], "total": Decimal("0.00")}
        incomes_grouped[category_name]["items"].append(income_item)
        incomes_grouped[category_name]["total"] += income_item.amount
        total_revenue += income_item.amount

    expenses = Expense.objects.filter(date__gte=start_date, date__lte=end_date).select_related("category").order_by("category__name", "date")
    expenses_grouped = {}
    total_expenditure = Decimal("0.00")
    for expense_item in expenses: # Renamed to avoid conflict
        category_name = expense_item.category.name if expense_item.category else "Sem Categoria"
        if category_name not in expenses_grouped:
            expenses_grouped[category_name] = {"items": [], "total": Decimal("0.00")}
        expenses_grouped[category_name]["items"].append(expense_item)
        expenses_grouped[category_name]["total"] += expense_item.amount
        total_expenditure += expense_item.amount

    final_balance = total_revenue - total_expenditure

    context = {
        "active_menu": "reports",
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
        "church_config": filters["church_config"],
    }

    return render(request, "reports/financeiro_categorias.html", context)

