from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomAuthenticationForm, CustomPasswordChangeForm

app_name = 'users'

urlpatterns = [
    # Autenticação
    path('login/', auth_views.LoginView.as_view(
        template_name='users/login.html',
        authentication_form=CustomAuthenticationForm
    ), name='login'),

    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Gerenciamento de usuários
    path('', views.user_list, name='user_list'),
    path('novo/', views.user_create, name='user_create'),
    path('<int:pk>/', views.user_detail, name='user_detail'),
    path('<int:pk>/editar/', views.user_update, name='user_update'),
    path('<int:pk>/excluir/', views.user_delete, name='user_delete'),

    # Perfil e senha
    path('perfil/', views.profile, name='profile'),
    path('alterar-senha/', auth_views.PasswordChangeView.as_view(
        template_name='users/password_change.html',
        form_class=CustomPasswordChangeForm,
        success_url='/users/perfil/'
    ), name='password_change'),

    # Recuperação de senha
    path('recuperar-senha/', auth_views.PasswordResetView.as_view(
        template_name='users/password_reset.html',
        email_template_name='users/password_reset_email.html',
        subject_template_name='users/password_reset_subject.txt',
        success_url='/users/recuperar-senha/enviado/'
    ), name='password_reset'),

    path('recuperar-senha/enviado/', auth_views.PasswordResetDoneView.as_view(
        template_name='users/password_reset_done.html'
    ), name='password_reset_done'),

    path('recuperar-senha/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='users/password_reset_confirm.html',
        success_url='/users/recuperar-senha/concluido/'
    ), name='password_reset_confirm'),

    path('recuperar-senha/concluido/', auth_views.PasswordResetCompleteView.as_view(
        template_name='users/password_reset_complete.html'
    ), name='password_reset_complete'),
]
