from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .decorators import admin_required

User = get_user_model()

@login_required
def profile(request):
    """
    Exibe o perfil do usuário logado.
    """
    return render(request, 'usuarios/profile.html', {
        'user': request.user,
        'active_menu': 'usuarios',
    })

@admin_required
def user_list(request):
    """
    Lista todos os usuários (apenas para administradores).
    """
    users = User.objects.all().order_by('first_name', 'last_name')
    return render(request, 'usuarios/user_list.html', {
        'users': users,
        'active_menu': 'usuarios',
    })

@admin_required
def user_detail(request, pk):
    """
    Exibe detalhes de um usuário específico (apenas para administradores).
    """
    user = get_object_or_404(User, pk=pk)
    return render(request, 'usuarios/user_detail.html', {
        'user_obj': user,  # Usando user_obj para evitar conflito com user do request
        'active_menu': 'usuarios',
    })

@admin_required
def user_create(request):
    """
    Cria um novo usuário (apenas para administradores).
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Usuário {user.username} criado com sucesso!')
            return redirect('usuarios:user_detail', pk=user.pk)
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'usuarios/user_form.html', {
        'form': form,
        'title': 'Novo Usuário',
        'active_menu': 'usuarios',
    })

@admin_required
def user_update(request, pk):
    """
    Atualiza um usuário existente (apenas para administradores).
    """
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuário {user.username} atualizado com sucesso!')
            return redirect('usuarios:user_detail', pk=user.pk)
    else:
        form = CustomUserChangeForm(instance=user)
    
    return render(request, 'usuarios/user_form.html', {
        'form': form,
        'user_obj': user,
        'title': 'Editar Usuário',
        'active_menu': 'usuarios',
    })

@admin_required
def user_delete(request, pk):
    """
    Exclui um usuário (apenas para administradores).
    """
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'Usuário {username} excluído com sucesso!')
        return redirect('usuarios:user_list')
    
    return render(request, 'usuarios/user_confirm_delete.html', {
        'user_obj': user,
        'active_menu': 'usuarios',
    })
