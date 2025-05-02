from django.db import models
from django.conf import settings
from churches.models import Church

class Member(models.Model):
    MEMBER_TYPE_CHOICES = [
        ("membro", "Membro"),
        ("visitante", "Visitante"),
        ("obreiro", "Obreiro"),
        # Adicionar outros tipos conforme necessário
    ]
    GENDER_CHOICES = [
        ("M", "Masculino"),
        ("F", "Feminino"),
        ("O", "Outro"),
    ]
    MARITAL_STATUS_CHOICES = [
        ("solteiro", "Solteiro(a)"),
        ("casado", "Casado(a)"),
        ("divorciado", "Divorciado(a)"),
        ("viuvo", "Viúvo(a)"),
    ]
    STATUS_CHOICES = [
        ("ativo", "Ativo"),
        ("inativo", "Inativo"),
        ("transferido", "Transferido"),
        ("disciplina", "Em Disciplina"),
        ("visitante", "Visitante"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuário do Sistema")
    name = models.CharField(max_length=255, verbose_name="Nome Completo")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Data de Nascimento")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True, verbose_name="Sexo")
    marital_status = models.CharField(max_length=15, choices=MARITAL_STATUS_CHOICES, null=True, blank=True, verbose_name="Estado Civil")
    address = models.TextField(blank=True, null=True, verbose_name="Endereço")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    baptism_date = models.DateField(null=True, blank=True, verbose_name="Data de Batismo")
    join_date = models.DateField(blank=True, null=True, verbose_name="Data de Ingresso")
    origin_church = models.CharField(max_length=255, blank=True, null=True, verbose_name="Igreja de Origem")
    member_type = models.CharField(max_length=50, choices=MEMBER_TYPE_CHOICES, default="membro", verbose_name="Tipo de Membro") # Pode ser redundante com role
    role = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cargo/Função")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="ativo", verbose_name="Status")
    church = models.ForeignKey(Church, on_delete=models.SET_NULL, null=True, blank=True, related_name="members", verbose_name="Igreja Atual")
    photo = models.ImageField(upload_to='member_photos/', null=True, blank=True, verbose_name="Foto")
    notes = models.TextField(blank=True, null=True, verbose_name="Observações")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Membro"
        verbose_name_plural = "Membros"
        ordering = ["name"]
