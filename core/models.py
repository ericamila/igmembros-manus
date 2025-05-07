from django.db import models

class ChurchConfiguration(models.Model):
    church_name = models.CharField(max_length=255, verbose_name="Nome da Igreja Sede")
    logo = models.ImageField(upload_to="church_logo/", blank=True, null=True, verbose_name="Logo da Igreja")
    president_pastor_name = models.CharField(max_length=255, blank=True, verbose_name="Nome do Pastor Presidente")
    treasurer_name = models.CharField(max_length=255, blank=True, verbose_name="Nome do Tesoureiro(a)")

    def __str__(self):
        return self.church_name or "Configuração da Igreja"

    class Meta:
        verbose_name = "Configuração da Igreja"
        verbose_name_plural = "Configurações da Igreja"

    # Garantir que apenas uma instância possa ser criada (Singleton)
    def save(self, *args, **kwargs):
        if not self.pk and ChurchConfiguration.objects.exists():
            # Não permitir criar uma nova instância se uma já existe
            raise ValidationError("Só pode existir uma configuração de igreja. Edite a existente.")
        return super(ChurchConfiguration, self).save(*args, **kwargs)

# Create your models here.

