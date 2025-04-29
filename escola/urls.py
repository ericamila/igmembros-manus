from django.urls import path
from . import views

app_name = 'escola'

urlpatterns = [
    # Rotas para Turmas (SchoolClass)
    path('turmas/', views.school_class_list, name='school_class_list'),
    path('turmas/nova/', views.school_class_create, name='school_class_create'),
    path('turmas/<int:pk>/', views.school_class_detail, name='school_class_detail'),
    path('turmas/<int:pk>/editar/', views.school_class_update, name='school_class_update'),
    path('turmas/<int:pk>/excluir/', views.school_class_delete, name='school_class_delete'),
    
    # Rotas para Alunos (Student)
    path('alunos/', views.student_list, name='student_list'),
    path('alunos/novo/', views.student_create, name='student_create'),
    path('alunos/<int:pk>/', views.student_detail, name='student_detail'),
    path('alunos/<int:pk>/editar/', views.student_update, name='student_update'),
    path('alunos/<int:pk>/excluir/', views.student_delete, name='student_delete'),
    
    # Rotas para Frequência (Attendance)
    path('frequencia/', views.attendance_list, name='attendance_list'),
    path('frequencia/nova/', views.attendance_create, name='attendance_create'),
    path('frequencia/<int:pk>/', views.attendance_detail, name='attendance_detail'),
    path('frequencia/<int:pk>/editar/', views.attendance_update, name='attendance_update'),
    path('frequencia/<int:pk>/excluir/', views.attendance_delete, name='attendance_delete'),
]
