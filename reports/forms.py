from django import forms
from django.forms import inlineformset_factory
from .models import AccountabilityReport, AccountabilityDocument

class AccountabilityReportForm(forms.ModelForm):
    class Meta:
        model = AccountabilityReport
        fields = ["month", "year", "amount"]
        widgets = {
            "month": forms.Select(attrs={"class": "form-select"}),
            "year": forms.NumberInput(attrs={"class": "form-input", "placeholder": "Ex: 2024"}),
            "amount": forms.NumberInput(attrs={"class": "form-input", "step": "0.01", "placeholder": "Valor total da prestação"}),
        }

class AccountabilityDocumentForm(forms.ModelForm):
    class Meta:
        model = AccountabilityDocument
        fields = ["document", "description"]
        widgets = {
        #   "document": forms.ClearableFileInput(attrs={"class": "form-input file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-purple-50 file:text-purple-700 hover:file:bg-purple-100", "multiple": True}), # Allow multiple files in theory, but formset handles one per form
            # Removed "multiple": True as ClearableFileInput doesn't support it directly with formsets
            "document": forms.ClearableFileInput(attrs={"class": "form-input file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-purple-50 file:text-purple-700 hover:file:bg-purple-100"}), 
            "description": forms.TextInput(attrs={"class": "form-input", "placeholder": "Descrição breve do documento"}),
        }

# Create a formset for handling multiple documents per report
# `extra=1` means show 1 empty form by default
AccountabilityDocumentFormSet = inlineformset_factory(
    AccountabilityReport, 
    AccountabilityDocument, 
    form=AccountabilityDocumentForm, 
    fields=["document", "description"], 
    extra=1, 
    can_delete=True # Allow deleting existing documents in update view
)

