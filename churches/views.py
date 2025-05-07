from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
# Removed unused login_required and method_decorator as Mixins are preferred for CBVs
from .models import Church
from .forms import ChurchForm

# ChurchListView e ChurchDetailView: Todos os perfis logados podem ver.
class ChurchListView(LoginRequiredMixin, ListView):
    model = Church
    template_name = 'churches/church_list.html'
    context_object_name = 'churches'
    paginate_by = 10 
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'churches'
        return context

class ChurchDetailView(LoginRequiredMixin, DetailView):
    model = Church
    template_name = 'churches/church_detail.html'
    context_object_name = 'church'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'churches'
        return context

# ChurchCreateView: Admin e Secretário podem criar.
class ChurchCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Church
    form_class = ChurchForm
    template_name = 'churches/church_form.html'
    success_url = reverse_lazy('churches:church_list')
    permission_required = 'churches.add_church'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Adicionar Nova Igreja'
        context['button_text'] = 'Adicionar Igreja'
        context['active_menu'] = 'churches'
        return context

# ChurchUpdateView: Admin e Secretário podem atualizar.
class ChurchUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Church
    form_class = ChurchForm
    template_name = 'churches/church_form.html'
    success_url = reverse_lazy('churches:church_list')
    permission_required = 'churches.change_church'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Editar Igreja: {self.object.name}'
        context['button_text'] = 'Salvar Alterações'
        context['active_menu'] = 'churches'
        return context

# ChurchDeleteView: Admin e Secretário podem deletar.
class ChurchDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Church
    template_name = 'churches/church_confirm_delete.html'
    success_url = reverse_lazy('churches:church_list')
    context_object_name = 'church'
    permission_required = 'churches.delete_church'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Confirmar Exclusão: {self.object.name}'
        context['active_menu'] = 'churches'
        return context

