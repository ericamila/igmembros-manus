from django.db import models
from igrejas.models import Church

class Event(models.Model):
    EVENT_TYPE_CHOICES = [
        ("culto", "Culto"),
        ("reuniao", "Reunião"),
        ("especial", "Especial"),
        # Adicionar outros tipos conforme necessário
    ]

    title = models.CharField(max_length=255, verbose_name="Título")
    date = models.DateField(verbose_name="Data")
    time = models.TimeField(blank=True, null=True, verbose_name="Hora")
    description = models.TextField(blank=True, null=True, verbose_name="Descrição")
    type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES, blank=True, null=True, verbose_name="Tipo de Evento")
    church = models.ForeignKey(Church, on_delete=models.CASCADE, related_name="events", verbose_name="Igreja")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    def __str__(self):
        return f"{self.title} - {self.date.strftime('%d/%m/%Y')}"

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ["date", "time"]

