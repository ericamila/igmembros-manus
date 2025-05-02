from django import forms
from .models import Member

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = [
            'name', 'birth_date', 'gender', 'marital_status', 'phone', 
            'email', 'address', 'baptism_date', 'join_date', 
            'origin_church', 'role', 'status', 'photo', 'notes', 'church', 'user', 'member_type'
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'baptism_date': forms.DateInput(attrs={'type': 'date'}),
            'join_date': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            # 'photo': forms.ClearableFileInput(), # Styling applied below
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adicionar classes Tailwind CSS
        tailwind_classes = 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-purple-500 focus:border-purple-500 sm:text-sm'
        tailwind_classes_file = 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-purple-50 file:text-purple-700 hover:file:bg-purple-100'
        
        # Ocultar ou desabilitar o campo 'user' se necessário (geralmente preenchido automaticamente)
        if 'user' in self.fields:
            self.fields['user'].widget = forms.HiddenInput()
            # Ou desabilitar:
            # self.fields['user'].disabled = True
            # self.fields['user'].required = False

        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.ClearableFileInput):
                field.widget.attrs['class'] = tailwind_classes_file
            elif isinstance(field.widget, forms.CheckboxInput):
                 field.widget.attrs['class'] = 'h-4 w-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500'
            elif isinstance(field.widget, forms.Textarea):
                 field.widget.attrs['class'] = f'{tailwind_classes} min-h-[80px]'
            elif isinstance(field.widget, (forms.DateInput, forms.Select)):
                 field.widget.attrs['class'] = f'{tailwind_classes} text-gray-700'
            elif not isinstance(field.widget, forms.HiddenInput): # Não aplicar a classe a campos ocultos
                field.widget.attrs['class'] = tailwind_classes
