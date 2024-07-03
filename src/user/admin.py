from django.contrib import admin
from .models import ServiceUser


@admin.register(ServiceUser)
class ServiceUserAdmin(admin.ModelAdmin):
    pass
