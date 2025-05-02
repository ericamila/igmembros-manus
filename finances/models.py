from django.db import models
from members.models import Member
from churches.models import Church

class Category(models.Model):
    TYPE_CHOICES = [
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
        ('ambos', 'Ambos'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Nome")
    category_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='ambos', verbose_name="Tipo")
    description = models.TextField(blank=True, null=True, verbose_name="Descrição")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['name']

class Income(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('dinheiro', 'Dinheiro'),
        ('pix', 'PIX'),
        ('cartao', 'Cartão'),
        ('transferencia', 'Transferência'),
        ('cheque', 'Cheque'),
        ('outro', 'Outro'),
    ]
    
    date = models.DateField(verbose_name="Data")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    description = models.CharField(max_length=255, verbose_name="Descrição")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name="Categoria")
    church = models.ForeignKey(Church, on_delete=models.CASCADE, verbose_name="Igreja")
    member = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Membro")
    payment_method = models.CharField(max_length=15, choices=PAYMENT_METHOD_CHOICES, default='dinheiro', verbose_name="Forma de Pagamento")
    receipt = models.FileField(upload_to='comprovantes/entradas/', null=True, blank=True, verbose_name="Comprovante")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    def __str__(self):
        return f"{self.description} - R$ {self.amount} ({self.date})"
    
    class Meta:
        verbose_name = "Entrada"
        verbose_name_plural = "Entradas"
        ordering = ['-date']

class Expense(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('dinheiro', 'Dinheiro'),
        ('pix', 'PIX'),
        ('cartao', 'Cartão'),
        ('transferencia', 'Transferência'),
        ('cheque', 'Cheque'),
        ('outro', 'Outro'),
    ]
    
    date = models.DateField(verbose_name="Data")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    description = models.CharField(max_length=255, verbose_name="Descrição")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name="Categoria")
    church = models.ForeignKey(Church, on_delete=models.CASCADE, verbose_name="Igreja")
    payment_method = models.CharField(max_length=15, choices=PAYMENT_METHOD_CHOICES, default='dinheiro', verbose_name="Forma de Pagamento")
    receipt = models.FileField(upload_to='comprovantes/saidas/', null=True, blank=True, verbose_name="Comprovante")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    def __str__(self):
        return f"{self.description} - R$ {self.amount} ({self.date})"
    
    class Meta:
        verbose_name = "Saída"
        verbose_name_plural = "Saídas"
        ordering = ['-date']

# Mantendo o modelo Donation para compatibilidade com código existente
class Donation(models.Model):
    member = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True, related_name="donations", verbose_name="Membro")
    church = models.ForeignKey(Church, on_delete=models.SET_NULL, null=True, blank=True, related_name="donations", verbose_name="Igreja")
    reference_date = models.DateField(verbose_name="Mês/Ano de Referência")
    tithes_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Dízimos")
    offerings_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Ofertas")
    projects_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Projetos Especiais")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    def __str__(self):
        return f"Doações - {self.reference_date.strftime('%m/%Y')} - {self.church or 'Geral'}"

    class Meta:
        verbose_name = "Registro Financeiro Mensal"
        verbose_name_plural = "Registros Financeiros Mensais"
        ordering = ["-reference_date", "church"]
