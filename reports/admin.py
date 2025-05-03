from django.contrib import admin

# Register your models here.
from .models import AccountabilityReport, AccountabilityDocument

admin.site.register(AccountabilityReport)
admin.site.register(AccountabilityDocument)
