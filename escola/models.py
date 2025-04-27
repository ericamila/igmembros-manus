from django.db import models
from membros.models import Member

class SchoolClass(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nome da Turma")
    description = models.TextField(blank=True, null=True, verbose_name="Descrição")
    # Usar Member como professor, assumindo que professores são membros
    teacher = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True, related_name="taught_classes", verbose_name="Professor")
    room = models.CharField(max_length=100, blank=True, null=True, verbose_name="Sala")
    schedule = models.CharField(max_length=255, blank=True, null=True, verbose_name="Horário")
    max_students = models.PositiveIntegerField(blank=True, null=True, verbose_name="Máximo de Alunos")
    # current_students pode ser calculado ou mantido via signals/métodos
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Turma da Escola Dominical"
        verbose_name_plural = "Turmas da Escola Dominical"
        ordering = ["name"]

class Student(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="student_enrollments", verbose_name="Membro (Aluno)")
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name="students", verbose_name="Turma")
    enrollment_date = models.DateField(auto_now_add=True, verbose_name="Data de Matrícula")
    # attendance_rate pode ser calculado
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    def __str__(self):
        return f"{self.member.name} - {self.school_class.name}"

    class Meta:
        verbose_name = "Aluno"
        verbose_name_plural = "Alunos"
        unique_together = [("member", "school_class")] # Um membro só pode estar em uma turma uma vez?
        ordering = ["school_class", "member__name"]

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendances", verbose_name="Aluno")
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name="attendances", verbose_name="Turma") # Redundante? Student já tem a turma.
    date = models.DateField(verbose_name="Data da Aula")
    present = models.BooleanField(default=False, verbose_name="Presente")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Registrado em")

    def __str__(self):
        status = "Presente" if self.present else "Ausente"
        return f"{self.student} - {self.date.strftime('%d/%m/%Y')} - {status}"

    class Meta:
        verbose_name = "Registro de Frequência"
        verbose_name_plural = "Registros de Frequência"
        unique_together = [("student", "date")] # Um aluno só tem um registro por dia
        ordering = ["-date", "student"]

