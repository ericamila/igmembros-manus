from django.db import models
from django.conf import settings
from igrejas.models import Church

class Member(models.Model):
    MEMBER_TYPE_CHOICES = [
        ("membro", "Membro"),
        ("visitante", "Visitante"),
        ("obreiro", "Obreiro"),
        # Adicionar outros tipos conforme necessário
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuário do Sistema")
    name = models.CharField(max_length=255, verbose_name="Nome Completo")
    address = models.TextField(blank=True, null=True, verbose_name="Endereço")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    join_date = models.DateField(blank=True, null=True, verbose_name="Data de Ingresso")
    member_type = models.CharField(max_length=50, choices=MEMBER_TYPE_CHOICES, default="membro", verbose_name="Tipo de Membro")
    church = models.ForeignKey(Church, on_delete=models.SET_NULL, null=True, blank=True, related_name="members", verbose_name="Igreja")
    # Adicionar outros campos relevantes, como data de nascimento, estado civil, etc.
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Membro"
        verbose_name_plural = "Membros"
        ordering = ["name"]
