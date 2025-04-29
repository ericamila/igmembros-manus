from django import forms
from .models import Entrada, Saida, Categoria

class EntradaForm(forms.ModelForm):
    class Meta:
        model = Entrada
        fields = ['data', 'valor', 'descricao', 'categoria', 'igreja', 'membro', 'forma_pagamento', 'comprovante']
        widgets = {
            'data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'igreja': forms.Select(attrs={'class': 'form-control'}),
            'membro': forms.Select(attrs={'class': 'form-control'}),
            'forma_pagamento': forms.Select(attrs={'class': 'form-control'}),
            'comprovante': forms.FileInput(attrs={'class': 'form-control'}),
        }

class SaidaForm(forms.ModelForm):
    class Meta:
        model = Saida
        fields = ['data', 'valor', 'descricao', 'categoria', 'igreja', 'forma_pagamento', 'comprovante']
        widgets = {
            'data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'igreja': forms.Select(attrs={'class': 'form-control'}),
            'forma_pagamento': forms.Select(attrs={'class': 'form-control'}),
            'comprovante': forms.FileInput(attrs={'class': 'form-control'}),
        }

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome', 'tipo', 'descricao']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
