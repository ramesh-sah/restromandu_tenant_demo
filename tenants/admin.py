from django.contrib import admin
from django_tenants.utils import get_public_schema_name
from django.db import connection
from .models import Client, Domain


class DomainInline(admin.TabularInline):
    model = Domain
    extra = 1


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "schema_name", "is_active", "created_at")
    list_filter = ("is_active",)
    inlines = [DomainInline]

    def has_module_permission(self, request):
        return connection.schema_name == get_public_schema_name()

    def has_view_permission(self, request, obj=None):
        return connection.schema_name == get_public_schema_name()
