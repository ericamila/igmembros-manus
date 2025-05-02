from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Member
from .forms import MemberForm as MemberForm # Temporarily alias

@method_decorator(login_required, name='dispatch')
class MemberListView(ListView):
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

@method_decorator(login_required, name='dispatch')
class MemberDetailView(DetailView):
    model = Member
    template_name = "members/member_detail.html"
    context_object_name = "member"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'members'
        return context

@method_decorator(login_required, name='dispatch')
class MemberCreateView(CreateView):
    model = Member
    form_class = MemberForm
    template_name = "members/member_form.html"
    success_url = reverse_lazy("members:member_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Adicionar Novo Member"
        context["button_text"] = "Adicionar Member"
        context['active_menu'] = 'members'
        return context

@method_decorator(login_required, name='dispatch')
class MemberUpdateView(UpdateView):
    model = Member
    form_class = MemberForm
    template_name = "members/member_form.html"
    success_url = reverse_lazy("members:member_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = f"Editar Member: {self.object.name}"
        context["button_text"] = "Salvar Alterações"
        context['active_menu'] = 'members'
        return context

@method_decorator(login_required, name='dispatch')
class MemberDeleteView(DeleteView):
    model = Member
    template_name = "members/member_confirm_delete.html"
    success_url = reverse_lazy("members:member_list")
    context_object_name = "member"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = f"Confirmar Exclusão: {self.object.name}"
        context['active_menu'] = 'members'
        return context
