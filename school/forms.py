from django import forms
from .models import SchoolClass, Student, Attendance
import datetime

class SchoolClassForm(forms.ModelForm):
    class Meta:
        model = SchoolClass
        fields = ["name", "description", "teacher", "room", "schedule", "max_students"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply Tailwind classes if needed, but base.html script handles basic inputs
        # for field_name, field in self.fields.items():
        #     field.widget.attrs.update({"class": "form-control"})

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["member", "school_class"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply Tailwind classes if needed
        # for field_name, field in self.fields.items():
        #     field.widget.attrs.update({"class": "form-control"})

# Form for recording attendance for a whole class on a specific date
class AttendanceRecordForm(forms.Form):
    date = forms.DateField(
        label="Data da Aula", 
        widget=forms.DateInput(attrs={"type": "date"}),
        initial=datetime.date.today
    )
    # Student presence will be handled via checkboxes in the template/view
    # We add a field to hold the class PK for processing
    school_class_pk = forms.IntegerField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        school_class = kwargs.pop("school_class", None)
        super().__init__(*args, **kwargs)
        if school_class:
            self.fields["school_class_pk"].initial = school_class.pk
        # Apply Tailwind classes if needed
        self.fields["date"].widget.attrs.update({"class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"})


# --- Old AttendanceForm (for individual records - might be removed later) ---
class OldAttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ["student", "school_class", "date", "present"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply Tailwind classes if needed
        # for field_name, field in self.fields.items():
        #     field.widget.attrs.update({"class": "form-control"})
            
    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get("student")
        school_class = cleaned_data.get("school_class")
        
        if student and school_class and student.school_class != school_class:
            raise forms.ValidationError("O aluno selecionado não pertence à turma selecionada.")
        
        return cleaned_data

