from django import forms
from .models import Church

class IgrejaForm(forms.ModelForm):
    class Meta:
        model = Church
        fields = [
            'name', 'type', 'address', 'phone', 'email', 
            'founded_date', 'schedule', 'description'
        ]
        widgets = {
            'founded_date': forms.DateInput(attrs={'type': 'date'}),
            'schedule': forms.Textarea(attrs={'rows': 3}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adicionar classes Tailwind CSS ou outras personalizações se necessário
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-purple-500 focus:border-purple-500 sm:text-sm'
            if isinstance(field.widget, forms.Textarea):
                 field.widget.attrs['class'] += ' min-h-[80px]'
            if isinstance(field.widget, forms.DateInput):
                 field.widget.attrs['class'] += ' text-gray-700'
            if isinstance(field.widget, forms.Select):
                 field.widget.attrs['class'] += ' text-gray-700'
