from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Church
from .forms import ChurchForm

@method_decorator(login_required, name='dispatch')
class ChurchListView(ListView):
    model = Church
    template_name = 'churches/church_list.html'
    context_object_name = 'churches'
    paginate_by = 10 
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'churches'
        return context

@method_decorator(login_required, name='dispatch')
class ChurchDetailView(DetailView):
    model = Church
    template_name = 'churches/church_detail.html'
    context_object_name = 'church'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'churches'
        return context

@method_decorator(login_required, name='dispatch')
class ChurchCreateView(CreateView):
    model = Church
    form_class = ChurchForm
    template_name = 'churches/church_form.html'
    success_url = reverse_lazy('churches:church_list') # Redireciona para a lista após sucesso

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Adicionar Nova Igreja'
        context['button_text'] = 'Adicionar Igreja'
        context['active_menu'] = 'churches'
        return context

@method_decorator(login_required, name='dispatch')
class ChurchUpdateView(UpdateView):
    model = Church
    form_class = ChurchForm
    template_name = 'churches/church_form.html'
    success_url = reverse_lazy('churches:church_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Editar Igreja: {self.object.name}'
        context['button_text'] = 'Salvar Alterações'
        context['active_menu'] = 'churches'
        return context

@method_decorator(login_required, name='dispatch')
class ChurchDeleteView(DeleteView):
    model = Church
    template_name = 'churches/church_confirm_delete.html'
    success_url = reverse_lazy('churches:church_list')
    context_object_name = 'church'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Confirmar Exclusão: {self.object.name}'
        context['active_menu'] = 'churches'
        return context
