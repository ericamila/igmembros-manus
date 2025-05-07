from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.utils.decorators import method_decorator
from .models import Member
from .forms import MemberForm

# MemberListView e MemberDetailView já usam @method_decorator(login_required, name='dispatch')
# Todos os perfis (Admin, Secretário, Tesoureiro) podem visualizar membros.
class MemberListView(LoginRequiredMixin, ListView):
    model = Member
    template_name = "members/member_list.html"
    context_object_name = "members"
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset().select_related("church")
        return queryset.order_by("name")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'members'
        return context

class MemberDetailView(LoginRequiredMixin, DetailView):
    model = Member
    template_name = "members/member_detail.html"
    context_object_name = "member"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'members'
        return context

# Admin e Secretário podem criar membros
class MemberCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Member
    form_class = MemberForm
    template_name = "members/member_form.html"
    success_url = reverse_lazy("members:member_list")
    permission_required = "members.add_member"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Adicionar Novo Membro"
        context["button_text"] = "Adicionar Membro"
        context['active_menu'] = 'members'
        return context

# Admin e Secretário podem atualizar membros
class MemberUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Member
    form_class = MemberForm
    template_name = "members/member_form.html"
    success_url = reverse_lazy("members:member_list")
    permission_required = "members.change_member"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = f"Editar Membro: {self.object.name}"
        context["button_text"] = "Salvar Alterações"
        context['active_menu'] = 'members'
        return context

# Admin e Secretário podem deletar membros
class MemberDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Member
    template_name = "members/member_confirm_delete.html"
    success_url = reverse_lazy("members:member_list")
    context_object_name = "member"
    permission_required = "members.delete_member"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = f"Confirmar Exclusão: {self.object.name}"
        context['active_menu'] = 'members'
        return context

