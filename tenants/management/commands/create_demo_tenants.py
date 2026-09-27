from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django_tenants.utils import tenant_context
from tenants.models import Client, Domain

TENANTS = [
    {"schema": "demo1", "name": "Demo Restaurant 1", "domain": "demo1.localhost"},
    {"schema": "demo2", "name": "Demo Restaurant 2", "domain": "demo2.localhost"},
]

class Command(BaseCommand):
    help = "Create two isolated demo tenants and tenant-local users."

    def handle(self, *args, **options):
        for item in TENANTS:
            tenant, created = Client.objects.get_or_create(
                schema_name=item["schema"],
                defaults={"name": item["name"]},
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created tenant schema: {tenant.schema_name}"))
            else:
                self.stdout.write(f"Tenant exists: {tenant.schema_name}")

            Domain.objects.update_or_create(
                domain=item["domain"],
                defaults={"tenant": tenant, "is_primary": True},
            )

            with tenant_context(tenant):
                User = get_user_model()
                user, user_created = User.objects.get_or_create(
                    username="admin",
                    defaults={"email": f"admin@{item['domain']}"},
                )
                if user_created:
                    user.set_password("admin123")
                    user.is_staff = True
                    user.is_superuser = True
                    user.save()
                Group.objects.get_or_create(name="Manager")
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Ready: http://{item['domain']}:8000/  |  admin / admin123"
                    )
                )
