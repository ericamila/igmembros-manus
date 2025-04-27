from django.db import models
from membros.models import Member
from igrejas.models import Church

class Donation(models.Model):
    # Simplificado inicialmente, pode ser expandido para transações individuais
    member = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True, related_name="donations", verbose_name="Membro")
    church = models.ForeignKey(Church, on_delete=models.SET_NULL, null=True, blank=True, related_name="donations", verbose_name="Igreja")
    month = models.DateField(verbose_name="Mês/Ano de Referência") # Usar DateField para representar o mês/ano
    tithes = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Dízimos")
    offerings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Ofertas")
    projects = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Projetos Especiais")
    # Adicionar data da doação se for registrar individualmente
    # donation_date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    def __str__(self):
        return f"Doações - {self.month.strftime('%m/%Y')} - {self.church or 'Geral'}"

    class Meta:
        verbose_name = "Registro Financeiro Mensal"
        verbose_name_plural = "Registros Financeiros Mensais"
        ordering = ["-month", "church"]

