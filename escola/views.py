from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import SchoolClass, Student, Attendance
from .forms import SchoolClassForm, StudentForm, AttendanceForm

# Views para SchoolClass (Turmas)
def school_class_list(request):
    classes = SchoolClass.objects.all().order_by('name')
    return render(request, 'escola/school_class_list.html', {
        'classes': classes,
        'active_menu': 'escola',
    })

def school_class_detail(request, pk):
    school_class = get_object_or_404(SchoolClass, pk=pk)
    students = school_class.students.all()
    return render(request, 'escola/school_class_detail.html', {
        'school_class': school_class,
        'students': students,
        'active_menu': 'escola',
    })

def school_class_create(request):
    if request.method == 'POST':
        form = SchoolClassForm(request.POST)
        if form.is_valid():
            school_class = form.save()
            messages.success(request, 'Turma criada com sucesso!')
            return redirect('escola:school_class_detail', pk=school_class.pk)
    else:
        form = SchoolClassForm()
    
    return render(request, 'escola/school_class_form.html', {
        'form': form,
        'title': 'Nova Turma',
        'active_menu': 'escola',
    })

def school_class_update(request, pk):
    school_class = get_object_or_404(SchoolClass, pk=pk)
    
    if request.method == 'POST':
        form = SchoolClassForm(request.POST, instance=school_class)
        if form.is_valid():
            form.save()
            messages.success(request, 'Turma atualizada com sucesso!')
            return redirect('escola:school_class_detail', pk=school_class.pk)
    else:
        form = SchoolClassForm(instance=school_class)
    
    return render(request, 'escola/school_class_form.html', {
        'form': form,
        'school_class': school_class,
        'title': 'Editar Turma',
        'active_menu': 'escola',
    })

def school_class_delete(request, pk):
    school_class = get_object_or_404(SchoolClass, pk=pk)
    
    if request.method == 'POST':
        school_class.delete()
        messages.success(request, 'Turma excluída com sucesso!')
        return redirect('escola:school_class_list')
    
    return render(request, 'escola/school_class_confirm_delete.html', {
        'school_class': school_class,
        'active_menu': 'escola',
    })

# Views para Student (Alunos)
def student_list(request):
    students = Student.objects.all().select_related('member', 'school_class')
    return render(request, 'escola/student_list.html', {
        'students': students,
        'active_menu': 'escola',
    })

def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    attendances = student.attendances.all().order_by('-date')
    return render(request, 'escola/student_detail.html', {
        'student': student,
        'attendances': attendances,
        'active_menu': 'escola',
    })

def student_create(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            messages.success(request, 'Aluno matriculado com sucesso!')
            return redirect('escola:student_detail', pk=student.pk)
    else:
        form = StudentForm()
    
    return render(request, 'escola/student_form.html', {
        'form': form,
        'title': 'Nova Matrícula',
        'active_menu': 'escola',
    })

def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Matrícula atualizada com sucesso!')
            return redirect('escola:student_detail', pk=student.pk)
    else:
        form = StudentForm(instance=student)
    
    return render(request, 'escola/student_form.html', {
        'form': form,
        'student': student,
        'title': 'Editar Matrícula',
        'active_menu': 'escola',
    })

def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    
    if request.method == 'POST':
        student.delete()
        messages.success(request, 'Matrícula excluída com sucesso!')
        return redirect('escola:student_list')
    
    return render(request, 'escola/student_confirm_delete.html', {
        'student': student,
        'active_menu': 'escola',
    })

# Views para Attendance (Frequência)
def attendance_list(request):
    attendances = Attendance.objects.all().select_related('student', 'school_class').order_by('-date')
    return render(request, 'escola/attendance_list.html', {
        'attendances': attendances,
        'active_menu': 'escola',
    })

def attendance_detail(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    return render(request, 'escola/attendance_detail.html', {
        'attendance': attendance,
        'active_menu': 'escola',
    })

def attendance_create(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            attendance = form.save()
            messages.success(request, 'Registro de frequência criado com sucesso!')
            return redirect('escola:attendance_detail', pk=attendance.pk)
    else:
        form = AttendanceForm()
    
    return render(request, 'escola/attendance_form.html', {
        'form': form,
        'title': 'Novo Registro de Frequência',
        'active_menu': 'escola',
    })

def attendance_update(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    
    if request.method == 'POST':
        form = AttendanceForm(request.POST, instance=attendance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registro de frequência atualizado com sucesso!')
            return redirect('escola:attendance_detail', pk=attendance.pk)
    else:
        form = AttendanceForm(instance=attendance)
    
    return render(request, 'escola/attendance_form.html', {
        'form': form,
        'attendance': attendance,
        'title': 'Editar Registro de Frequência',
        'active_menu': 'escola',
    })

def attendance_delete(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    
    if request.method == 'POST':
        attendance.delete()
        messages.success(request, 'Registro de frequência excluído com sucesso!')
        return redirect('escola:attendance_list')
    
    return render(request, 'escola/attendance_confirm_delete.html', {
        'attendance': attendance,
        'active_menu': 'escola',
    })
