from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required # Ou LoginRequiredMixin para CBV
from django.contrib.admin.views.decorators import staff_member_required # Para restringir a admins
from django.views.generic import UpdateView, CreateView
from django.contrib import messages
from .models import ChurchConfiguration
from .forms import ChurchConfigurationForm

# Create your views here.

@login_required
# @staff_member_required # Descomente se apenas staff/admin pode configurar
def church_configuration_view(request):
    # Tenta obter a configuração existente ou cria uma nova se não existir (para o primeiro acesso)
    # A lógica de singleton no model impede múltiplas criações diretas, mas aqui garantimos que sempre haja uma para editar.
    config, created = ChurchConfiguration.objects.get_or_create(
        pk=1, # Assumindo que sempre usaremos pk=1 para a única configuração
        defaults={'church_name': 'Minha Igreja (Edite este Nome)'} # Valor padrão inicial
    )
    
    if request.method == 'POST':
        form = ChurchConfigurationForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, "Configurações da igreja atualizadas com sucesso!")
            return redirect("core:church_config") # Redireciona para a mesma página
        else:
            messages.error(request, "Erro ao atualizar as configurações. Verifique os campos.")
    else:
        form = ChurchConfigurationForm(instance=config)
        
    return render(request, "core/church_configuration_form.html", {"form": form, "config": config})


