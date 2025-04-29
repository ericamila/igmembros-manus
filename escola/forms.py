from django import forms
from .models import SchoolClass, Student, Attendance

class SchoolClassForm(forms.ModelForm):
    class Meta:
        model = SchoolClass
        fields = ['name', 'description', 'teacher', 'room', 'schedule', 'max_students']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['member', 'school_class']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['student', 'school_class', 'date', 'present']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
            
    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get('student')
        school_class = cleaned_data.get('school_class')
        
        if student and school_class and student.school_class != school_class:
            raise forms.ValidationError("O aluno selecionado não pertence à turma selecionada.")
        
        return cleaned_data
