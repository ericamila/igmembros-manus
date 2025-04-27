from django.db import models

class Church(models.Model):
    TYPE_CHOICES = [
        ('sede', 'Sede'),
        ('filial', 'Filial'),
    ]

    name = models.CharField(max_length=255, verbose_name="Nome")
    address = models.TextField(blank=True, null=True, verbose_name="Endereço")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    founded_date = models.DateField(blank=True, null=True, verbose_name="Data de Fundação")
    schedule = models.TextField(blank=True, null=True, verbose_name="Horários")
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, blank=True, null=True, verbose_name="Tipo")
    description = models.TextField(blank=True, null=True, verbose_name="Descrição")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Igreja"
        verbose_name_plural = "Igrejas"
        ordering = ['name']

