from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import os

# Function to validate allowed file extensions
def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # Get file extension
    valid_extensions = [".pdf", ".jpg", ".jpeg", ".png", ".gif", ".xls", ".xlsx"]
    if not ext.lower() in valid_extensions:
        raise ValidationError(_("Tipo de arquivo não suportado. Use PDF, JPG, PNG, GIF, XLS ou XLSX."))

# Model for Accountability Report
class AccountabilityReport(models.Model):
    month = models.IntegerField(_("Mês"), choices=[(i, i) for i in range(1, 13)])
    year = models.IntegerField(_("Ano"))
    amount = models.DecimalField(_("Valor Total"), max_digits=12, decimal_places=2, default=0.00)
    # Optional: Link to a specific church or keep it general?
    # church = models.ForeignKey("igrejas.Church", on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Igreja"))
    # Optional: Link to the user who created it
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Usuário"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Criado em"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Atualizado em"))

    def __str__(self):
        return f"Prestação de Contas - {self.month:02d}/{self.year}"

    class Meta:
        verbose_name = _("Prestação de Contas")
        verbose_name_plural = _("Prestações de Contas")
        ordering = ["-year", "-month"]
        unique_together = [["month", "year"]] # Ensure only one report per month/year

# Model for Documents associated with an Accountability Report
class AccountabilityDocument(models.Model):
    report = models.ForeignKey(AccountabilityReport, related_name="documents", on_delete=models.CASCADE, verbose_name=_("Prestação de Contas"))
    # Use the validator for the file field
    document = models.FileField(_("Documento"), upload_to="accountability_documents/%Y/%m/", validators=[validate_file_extension])
    description = models.CharField(_("Descrição"), max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Enviado em"))

    def __str__(self):
        return os.path.basename(self.document.name)

    class Meta:
        verbose_name = _("Documento de Prestação de Contas")
        verbose_name_plural = _("Documentos de Prestação de Contas")
        ordering = ["uploaded_at"]

