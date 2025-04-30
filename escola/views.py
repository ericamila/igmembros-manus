from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.utils.dateparse import parse_date
from .models import SchoolClass, Student, Attendance
from .forms import SchoolClassForm, StudentForm, AttendanceRecordForm # Import the new form
# from .forms import OldAttendanceForm # Keep if needed

# Views para SchoolClass (Turmas)
def school_class_list(request):
    classes = SchoolClass.objects.all().order_by("name")
    return render(request, "escola/school_class_list.html", {
        "classes": classes,
        "active_menu": "escola",
    })

def school_class_detail(request, pk):
    school_class = get_object_or_404(SchoolClass, pk=pk)
    students = school_class.students.select_related("member").order_by("member__name")
    # Get recent attendance dates for this class to show history (optional)
    recent_attendance_dates = Attendance.objects.filter(school_class=school_class).dates("date", "day", order="DESC")[:5]
    return render(request, "escola/school_class_detail.html", {
        "school_class": school_class,
        "students": students,
        "recent_attendance_dates": recent_attendance_dates,
        "active_menu": "escola",
    })

def school_class_create(request):
    if request.method == "POST":
        form = SchoolClassForm(request.POST)
        if form.is_valid():
            school_class = form.save()
            messages.success(request, "Turma criada com sucesso!")
            return redirect("escola:school_class_detail", pk=school_class.pk)
    else:
        form = SchoolClassForm()
    
    return render(request, "escola/school_class_form.html", {
        "form": form,
        "title": "Nova Turma",
        "active_menu": "escola",
    })

def school_class_update(request, pk):
    school_class = get_object_or_404(SchoolClass, pk=pk)
    
    if request.method == "POST":
        form = SchoolClassForm(request.POST, instance=school_class)
        if form.is_valid():
            form.save()
            messages.success(request, "Turma atualizada com sucesso!")
            return redirect("escola:school_class_detail", pk=school_class.pk)
    else:
        form = SchoolClassForm(instance=school_class)
    
    return render(request, "escola/school_class_form.html", {
        "form": form,
        "school_class": school_class,
        "title": "Editar Turma",
        "active_menu": "escola",
    })

def school_class_delete(request, pk):
    school_class = get_object_or_404(SchoolClass, pk=pk)
    
    if request.method == "POST":
        school_class.delete()
        messages.success(request, "Turma excluída com sucesso!")
        return redirect("escola:school_class_list")
    
    return render(request, "escola/school_class_confirm_delete.html", {
        "school_class": school_class,
        "active_menu": "escola",
    })

# Views para Student (Alunos)
def student_list(request):
    # Filter students by class if class_pk is provided in query params
    class_pk = request.GET.get("class_pk")
    students = Student.objects.all().select_related("member", "school_class").order_by("school_class__name", "member__name")
    school_class = None
    if class_pk:
        school_class = get_object_or_404(SchoolClass, pk=class_pk)
        students = students.filter(school_class=school_class)
        
    return render(request, "escola/student_list.html", {
        "students": students,
        "school_class": school_class, # Pass class to template if filtered
        "active_menu": "escola",
    })

def student_detail(request, pk):
    student = get_object_or_404(Student.objects.select_related("member", "school_class"), pk=pk)
    attendances = student.attendances.all().order_by("-date")
    return render(request, "escola/student_detail.html", {
        "student": student,
        "attendances": attendances,
        "active_menu": "escola",
    })

def student_create(request):
    # Optionally pre-fill class if coming from class detail page
    initial_data = {}
    class_pk = request.GET.get("class_pk")
    if class_pk:
        initial_data["school_class"] = class_pk
        
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            messages.success(request, f"Aluno {student.member.name} matriculado com sucesso na turma {student.school_class.name}!")
            # Redirect back to class detail page if class_pk was provided
            if class_pk:
                 return redirect("escola:school_class_detail", pk=class_pk)
            else:
                 return redirect("escola:student_detail", pk=student.pk)
    else:
        form = StudentForm(initial=initial_data)
    
    return render(request, "escola/student_form.html", {
        "form": form,
        "title": "Nova Matrícula",
        "active_menu": "escola",
    })

def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    
    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Matrícula atualizada com sucesso!")
            return redirect("escola:student_detail", pk=student.pk)
    else:
        form = StudentForm(instance=student)
    
    return render(request, "escola/student_form.html", {
        "form": form,
        "student": student,
        "title": "Editar Matrícula",
        "active_menu": "escola",
    })

def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    class_pk = student.school_class.pk # Get class pk before deleting student
    
    if request.method == "POST":
        member_name = student.member.name
        student.delete()
        messages.success(request, f"Matrícula de {member_name} excluída com sucesso!")
        # Redirect back to class detail page
        return redirect("escola:school_class_detail", pk=class_pk)
    
    return render(request, "escola/student_confirm_delete.html", {
        "student": student,
        "active_menu": "escola",
    })

# --- New View for Recording Class Attendance ---
def record_class_attendance(request, class_pk):
    school_class = get_object_or_404(SchoolClass, pk=class_pk)
    students = school_class.students.select_related("member").order_by("member__name")
    
    if request.method == "POST":
        form = AttendanceRecordForm(request.POST, school_class=school_class)
        if form.is_valid():
            attendance_date = form.cleaned_data["date"]
            present_student_pks = request.POST.getlist("present_students") # Get list of PKs from checkboxes
            
            try:
                with transaction.atomic(): # Ensure all updates happen or none
                    for student in students:
                        is_present = str(student.pk) in present_student_pks
                        # Update or create attendance record for this student on this date
                        Attendance.objects.update_or_create(
                            student=student,
                            school_class=school_class, # Store class for easier filtering later
                            date=attendance_date,
                            defaults={"present": is_present}
                        )
                messages.success(request, f'Frequência para {school_class.name} em {attendance_date.strftime("%d/%m/%Y")} registrada com sucesso!')
                return redirect("escola:school_class_detail", pk=class_pk)
            except Exception as e:
                messages.error(request, f"Erro ao registrar frequência: {e}")
                # Stay on the same page or redirect with error
    else:
        # Check if a date is provided in GET to pre-fill or show existing records
        initial_date_str = request.GET.get("date")
        initial_date = parse_date(initial_date_str) if initial_date_str else None
        form = AttendanceRecordForm(school_class=school_class, initial={"date": initial_date} if initial_date else {})
        
        # Load existing attendance for the initial date to pre-check boxes
        existing_attendance = {}
        if initial_date:
            existing_records = Attendance.objects.filter(school_class=school_class, date=initial_date, present=True)
            existing_attendance = {record.student.pk for record in existing_records}

    return render(request, "escola/attendance_record_form.html", {
        "form": form,
        "school_class": school_class,
        "students": students,
        "existing_attendance": existing_attendance, # Pass existing records to template
        "active_menu": "escola",
    })

# --- Old Attendance Views (Keep or remove later) ---
# def attendance_list(request):
#     attendances = Attendance.objects.all().select_related("student", "school_class").order_by("-date")
#     return render(request, "escola/attendance_list.html", {
#         "attendances": attendances,
#         "active_menu": "escola",
#     })

# def attendance_detail(request, pk):
#     attendance = get_object_or_404(Attendance, pk=pk)
#     return render(request, "escola/attendance_detail.html", {
#         "attendance": attendance,
#         "active_menu": "escola",
#     })

# def attendance_create(request):
#     if request.method == "POST":
#         form = OldAttendanceForm(request.POST)
#         if form.is_valid():
#             attendance = form.save()
#             messages.success(request, "Registro de frequência criado com sucesso!")
#             return redirect("escola:attendance_detail", pk=attendance.pk)
#     else:
#         form = OldAttendanceForm()
#     
#     return render(request, "escola/attendance_form.html", {
#         "form": form,
#         "title": "Novo Registro de Frequência",
#         "active_menu": "escola",
#     })

# def attendance_update(request, pk):
#     attendance = get_object_or_404(Attendance, pk=pk)
#     
#     if request.method == "POST":
#         form = OldAttendanceForm(request.POST, instance=attendance)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Registro de frequência atualizado com sucesso!")
#             return redirect("escola:attendance_detail", pk=attendance.pk)
#     else:
#         form = OldAttendanceForm(instance=attendance)
#     
#     return render(request, "escola/attendance_form.html", {
#         "form": form,
#         "attendance": attendance,
#         "title": "Editar Registro de Frequência",
#         "active_menu": "escola",
#     })

# def attendance_delete(request, pk):
#     attendance = get_object_or_404(Attendance, pk=pk)
#     
#     if request.method == "POST":
#         attendance.delete()
#         messages.success(request, "Registro de frequência excluído com sucesso!")
#         return redirect("escola:attendance_list")
#     
#     return render(request, "escola/attendance_confirm_delete.html", {
#         "attendance": attendance,
#         "active_menu": "escola",
#     })

