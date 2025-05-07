from django import forms
from .models import ChurchConfiguration

class ChurchConfigurationForm(forms.ModelForm):
    class Meta:
        model = ChurchConfiguration
        fields = ["church_name", "logo", "president_pastor_name", "treasurer_name"]
        widgets = {
            "church_name": forms.TextInput(attrs={"class": "form-control"}),
            "logo": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "president_pastor_name": forms.TextInput(attrs={"class": "form-control"}),
            "treasurer_name": forms.TextInput(attrs={"class": "form-control"}),
        }

