from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.utils.dateparse import parse_date
from django.contrib.auth.decorators import login_required, permission_required

from .models import SchoolClass, Student, Attendance # Corrected model name to Attendance
from .forms import SchoolClassForm, StudentForm, AttendanceRecordForm

# Views para SchoolClass (Turmas)
@login_required
def school_class_list(request):
    classes = SchoolClass.objects.all().order_by("name")
    return render(request, "schools/school_class_list.html", {
        "classes": classes,
        "active_menu": "school",
    })

@login_required
def school_class_detail(request, pk):
    school_class = get_object_or_404(SchoolClass, pk=pk)
    students = school_class.students.select_related("member").order_by("member__name")
    recent_attendance_dates = Attendance.objects.filter(school_class=school_class).dates("date", "day", order="DESC")[:5]
    return render(request, "schools/school_class_detail.html", {
        "school_class": school_class,
        "students": students,
        "recent_attendance_dates": recent_attendance_dates,
        "active_menu": "school",
    })

@login_required
@permission_required("school.add_schoolclass", raise_exception=True)
def school_class_create(request):
    if request.method == "POST":
        form = SchoolClassForm(request.POST)
        if form.is_valid():
            school_class = form.save()
            messages.success(request, "Turma criada com sucesso!")
            return redirect("school:school_class_detail", pk=school_class.pk)
    else:
        form = SchoolClassForm()
    
    return render(request, "schools/school_class_form.html", {
        "form": form,
        "title": "Nova Turma",
        "active_menu": "school",
    })

@login_required
@permission_required("school.change_schoolclass", raise_exception=True)
def school_class_update(request, pk):
    school_class = get_object_or_404(SchoolClass, pk=pk)
    
    if request.method == "POST":
        form = SchoolClassForm(request.POST, instance=school_class)
        if form.is_valid():
            form.save()
            messages.success(request, "Turma atualizada com sucesso!")
            return redirect("school:school_class_detail", pk=school_class.pk)
    else:
        form = SchoolClassForm(instance=school_class)
    
    return render(request, "schools/school_class_form.html", {
        "form": form,
        "school_class": school_class,
        "title": "Editar Turma",
        "active_menu": "school",
    })

@login_required
@permission_required("school.delete_schoolclass", raise_exception=True)
def school_class_delete(request, pk):
    school_class = get_object_or_404(SchoolClass, pk=pk)
    
    if request.method == "POST":
        school_class.delete()
        messages.success(request, "Turma excluída com sucesso!")
        return redirect("school:school_class_list")
    
    return render(request, "schools/school_class_confirm_delete.html", {
        "school_class": school_class,
        "active_menu": "school",
    })

# Views para Student (Alunos)
@login_required
def student_list(request):
    class_pk = request.GET.get("class_pk")
    students = Student.objects.all().select_related("member", "school_class").order_by("school_class__name", "member__name")
    school_class_filter = None # Renamed to avoid conflict
    if class_pk:
        school_class_filter = get_object_or_404(SchoolClass, pk=class_pk)
        students = students.filter(school_class=school_class_filter)
        
    return render(request, "schools/student_list.html", {
        "students": students,
        "school_class_filter": school_class_filter,
        "active_menu": "school",
    })

@login_required
def student_detail(request, pk):
    student = get_object_or_404(Student.objects.select_related("member", "school_class"), pk=pk)
    attendances = student.attendances.all().order_by("-date") # Use the correct related name
    return render(request, "schools/student_detail.html", {
        "student": student,
        "attendances": attendances,
        "active_menu": "school",
    })

@login_required
@permission_required("school.add_student", raise_exception=True)
def student_create(request):
    initial_data = {}
    class_pk = request.GET.get("class_pk")
    if class_pk:
        initial_data["school_class"] = class_pk
        
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            messages.success(request, f"Aluno {student.member.name} matriculado com sucesso na turma {student.school_class.name}!")
            if class_pk:
                 return redirect("school:school_class_detail", pk=class_pk)
            else:
                 return redirect("school:student_detail", pk=student.pk)
    else:
        form = StudentForm(initial=initial_data)
    
    return render(request, "schools/student_form.html", {
        "form": form,
        "title": "Nova Matrícula",
        "active_menu": "school",
    })

@login_required
@permission_required("school.change_student", raise_exception=True)
def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    
    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Matrícula atualizada com sucesso!")
            return redirect("school:student_detail", pk=student.pk)
    else:
        form = StudentForm(instance=student)
    
    return render(request, "schools/student_form.html", {
        "form": form,
        "student": student,
        "title": "Editar Matrícula",
        "active_menu": "school",
    })

@login_required
@permission_required("school.delete_student", raise_exception=True)
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    class_pk = student.school_class.pk
    
    if request.method == "POST":
        member_name = student.member.name
        student.delete()
        messages.success(request, f"Matrícula de {member_name} excluída com sucesso!")
        return redirect("school:school_class_detail", pk=class_pk)
    
    return render(request, "schools/student_confirm_delete.html", {
        "student": student,
        "active_menu": "school",
    })

@login_required
@permission_required("school.add_attendancerecord", raise_exception=True) # Assuming add implies change for update_or_create
def record_class_attendance(request, class_pk):
    school_class_obj = get_object_or_404(SchoolClass, pk=class_pk) # Renamed to avoid conflict
    students = school_class_obj.students.select_related("member").order_by("member__name")
    
    if request.method == "POST":
        form = AttendanceRecordForm(request.POST, school_class=school_class_obj)
        if form.is_valid():
            attendance_date = form.cleaned_data["date"]
            present_student_pks = request.POST.getlist("present_students")
            
            try:
                with transaction.atomic():
                    for student_obj in students: # Renamed to avoid conflict
                        is_present = str(student_obj.pk) in present_student_pks
                        Attendance.objects.update_or_create(
                            student=student_obj,
                            school_class=school_class_obj,
                            date=attendance_date,
                            defaults={"present": is_present}
                        )
                messages.success(request, f"Frequência para {school_class_obj.name} em {attendance_date.strftime('%d/%m/%Y')} registrada com sucesso!")
                return redirect("school:school_class_detail", pk=class_pk)
            except Exception as e:
                messages.error(request, f"Erro ao registrar frequência: {e}")
    else:
        initial_date_str = request.GET.get("date")
        initial_date = parse_date(initial_date_str) if initial_date_str else None
        form = AttendanceRecordForm(school_class=school_class_obj, initial={"date": initial_date} if initial_date else {})
        
        existing_attendance = {}
        if initial_date:
            existing_records = Attendance.objects.filter(school_class=school_class_obj, date=initial_date, present=True)
            existing_attendance = {record.student.pk for record in existing_records}

    return render(request, "schools/attendance_record_form.html", {
        "form": form,
        "school_class": school_class_obj, # Pass the renamed variable
        "students": students,
        "existing_attendance": existing_attendance,
        "active_menu": "school",
    })

