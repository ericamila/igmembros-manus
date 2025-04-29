from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    """
    Modelo de usuário personalizado que estende o modelo de usuário padrão do Django.
    """
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('pastor', 'Pastor'),
        ('secretario', 'Secretário'),
        ('tesoureiro', 'Tesoureiro'),
        ('lider', 'Líder'),
        ('membro', 'Membro'),
    ]
    
    role = models.CharField(
        _('Função'),
        max_length=20,
        choices=ROLE_CHOICES,
        default='membro',
        help_text=_('Define o nível de permissão do usuário no sistema')
    )
    
    phone = models.CharField(
        _('Telefone'),
        max_length=20,
        blank=True,
        null=True
    )
    
    address = models.TextField(
        _('Endereço'),
        blank=True,
        null=True
    )
    
    profile_image = models.ImageField(
        _('Imagem de Perfil'),
        upload_to='profile_images/',
        blank=True,
        null=True
    )
    
    def __str__(self):
        return self.get_full_name() or self.username
    
    class Meta:
        verbose_name = _('Usuário')
        verbose_name_plural = _('Usuários')
