from django import forms
from .models import Member

class MembroForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = [
            'name', 'address', 'phone', 'email', 'join_date', 
            'member_type', 'church'
        ]
        widgets = {
            'join_date': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adicionar classes Tailwind CSS
        tailwind_classes = 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-purple-500 focus:border-purple-500 sm:text-sm'
        tailwind_classes_file = 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-purple-50 file:text-purple-700 hover:file:bg-purple-100'
        
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.ClearableFileInput):
                field.widget.attrs['class'] = tailwind_classes_file
            elif isinstance(field.widget, forms.CheckboxInput):
                 # Checkbox styling might need specific handling or a custom widget/template tag
                 field.widget.attrs['class'] = 'h-4 w-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500'
            elif isinstance(field.widget, forms.Textarea):
                 field.widget.attrs['class'] = f'{tailwind_classes} min-h-[80px]'
            elif isinstance(field.widget, (forms.DateInput, forms.Select)):
                 field.widget.attrs['class'] = f'{tailwind_classes} text-gray-700'
            else:
                field.widget.attrs['class'] = tailwind_classes
