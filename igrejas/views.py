from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Church
from .forms import IgrejaForm

class IgrejaListView(ListView):
    model = Church
    template_name = 'igrejas/igreja_list.html'
    context_object_name = 'igrejas'
    paginate_by = 10 # Opcional: adicionar paginação
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'igrejas'
        return context

class IgrejaDetailView(DetailView):
    model = Church
    template_name = 'igrejas/igreja_detail.html'
    context_object_name = 'igreja'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'igrejas'
        return context

class IgrejaCreateView(CreateView):
    model = Church
    form_class = IgrejaForm
    template_name = 'igrejas/igreja_form.html'
    success_url = reverse_lazy('igrejas:igreja_list') # Redireciona para a lista após sucesso

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Adicionar Nova Igreja'
        context['texto_botao'] = 'Adicionar Igreja'
        context['active_menu'] = 'igrejas'
        return context

class IgrejaUpdateView(UpdateView):
    model = Church
    form_class = IgrejaForm
    template_name = 'igrejas/igreja_form.html'
    success_url = reverse_lazy('igrejas:igreja_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = f'Editar Igreja: {self.object.name}'
        context['texto_botao'] = 'Salvar Alterações'
        context['active_menu'] = 'igrejas'
        return context

class IgrejaDeleteView(DeleteView):
    model = Church
    template_name = 'igrejas/igreja_confirm_delete.html'
    success_url = reverse_lazy('igrejas:igreja_list')
    context_object_name = 'igreja'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = f'Confirmar Exclusão: {self.object.name}'
        context['active_menu'] = 'igrejas'
        return context
