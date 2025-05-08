from django.contrib import admin

# Register your models here.
from .models import SchoolClass, Student, Attendance

admin.site.register(SchoolClass)
admin.site.register(Student)
admin.site.register(Attendance)