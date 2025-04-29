from django.db import models
from membros.models import Member
from igrejas.models import Church

class Categoria(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
        ('ambos', 'Ambos'),
    ]
    
    nome = models.CharField(max_length=100, verbose_name="Nome")
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='ambos', verbose_name="Tipo")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['nome']

class Entrada(models.Model):
    FORMA_PAGAMENTO_CHOICES = [
        ('dinheiro', 'Dinheiro'),
        ('pix', 'PIX'),
        ('cartao', 'Cartão'),
        ('transferencia', 'Transferência'),
        ('cheque', 'Cheque'),
        ('outro', 'Outro'),
    ]
    
    data = models.DateField(verbose_name="Data")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    descricao = models.CharField(max_length=255, verbose_name="Descrição")
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, verbose_name="Categoria")
    igreja = models.ForeignKey(Church, on_delete=models.CASCADE, verbose_name="Igreja")
    membro = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Membro")
    forma_pagamento = models.CharField(max_length=15, choices=FORMA_PAGAMENTO_CHOICES, default='dinheiro', verbose_name="Forma de Pagamento")
    comprovante = models.FileField(upload_to='comprovantes/entradas/', null=True, blank=True, verbose_name="Comprovante")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    def __str__(self):
        return f"{self.descricao} - R$ {self.valor} ({self.data})"
    
    class Meta:
        verbose_name = "Entrada"
        verbose_name_plural = "Entradas"
        ordering = ['-data']

class Saida(models.Model):
    FORMA_PAGAMENTO_CHOICES = [
        ('dinheiro', 'Dinheiro'),
        ('pix', 'PIX'),
        ('cartao', 'Cartão'),
        ('transferencia', 'Transferência'),
        ('cheque', 'Cheque'),
        ('outro', 'Outro'),
    ]
    
    data = models.DateField(verbose_name="Data")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    descricao = models.CharField(max_length=255, verbose_name="Descrição")
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, verbose_name="Categoria")
    igreja = models.ForeignKey(Church, on_delete=models.CASCADE, verbose_name="Igreja")
    forma_pagamento = models.CharField(max_length=15, choices=FORMA_PAGAMENTO_CHOICES, default='dinheiro', verbose_name="Forma de Pagamento")
    comprovante = models.FileField(upload_to='comprovantes/saidas/', null=True, blank=True, verbose_name="Comprovante")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    def __str__(self):
        return f"{self.descricao} - R$ {self.valor} ({self.data})"
    
    class Meta:
        verbose_name = "Saída"
        verbose_name_plural = "Saídas"
        ordering = ['-data']

# Mantendo o modelo Donation para compatibilidade com código existente
class Donation(models.Model):
    member = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True, related_name="donations", verbose_name="Membro")
    church = models.ForeignKey(Church, on_delete=models.SET_NULL, null=True, blank=True, related_name="donations", verbose_name="Igreja")
    month = models.DateField(verbose_name="Mês/Ano de Referência")
    tithes = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Dízimos")
    offerings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Ofertas")
    projects = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Projetos Especiais")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    def __str__(self):
        return f"Doações - {self.month.strftime('%m/%Y')} - {self.church or 'Geral'}"

    class Meta:
        verbose_name = "Registro Financeiro Mensal"
        verbose_name_plural = "Registros Financeiros Mensais"
        ordering = ["-month", "church"]
