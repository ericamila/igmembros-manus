from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Member
from .forms import MembroForm

@method_decorator(login_required, name='dispatch')
class MembroListView(ListView):
    model = Member
    template_name = "membros/membro_list.html"
    context_object_name = "membros"
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset().select_related("church")
        return queryset.order_by("name")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'membros'
        return context

@method_decorator(login_required, name='dispatch')
class MembroDetailView(DetailView):
    model = Member
    template_name = "membros/membro_detail.html"
    context_object_name = "membro"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'membros'
        return context

@method_decorator(login_required, name='dispatch')
class MembroCreateView(CreateView):
    model = Member
    form_class = MembroForm
    template_name = "membros/membro_form.html"
    success_url = reverse_lazy("membros:membro_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo_pagina"] = "Adicionar Novo Membro"
        context["texto_botao"] = "Adicionar Membro"
        context['active_menu'] = 'membros'
        return context

@method_decorator(login_required, name='dispatch')
class MembroUpdateView(UpdateView):
    model = Member
    form_class = MembroForm
    template_name = "membros/membro_form.html"
    success_url = reverse_lazy("membros:membro_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo_pagina"] = f"Editar Membro: {self.object.name}"
        context["texto_botao"] = "Salvar Alterações"
        context['active_menu'] = 'membros'
        return context

@method_decorator(login_required, name='dispatch')
class MembroDeleteView(DeleteView):
    model = Member
    template_name = "membros/membro_confirm_delete.html"
    success_url = reverse_lazy("membros:membro_list")
    context_object_name = "membro"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo_pagina"] = f"Confirmar Exclusão: {self.object.name}"
        context['active_menu'] = 'membros'
        return context
