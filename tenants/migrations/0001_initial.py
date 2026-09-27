from django.db import migrations, models
import django_tenants.models

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="Client",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("schema_name", models.CharField(db_index=True, max_length=63, unique=True, verbose_name="Schema name")),
                ("name", models.CharField(max_length=150)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["name"]},
            bases=(django_tenants.models.TenantMixin, models.Model),
        ),
        migrations.CreateModel(
            name="Domain",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("domain", models.CharField(max_length=253, unique=True, verbose_name="Domain name")),
                ("is_primary", models.BooleanField(default=True, verbose_name="Is primary")),
                ("tenant", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="domains", to="tenants.client", verbose_name="Tenant")),
            ],
            options={"verbose_name": "Domain", "verbose_name_plural": "Domains"},
            bases=(django_tenants.models.DomainMixin, models.Model),
        ),
    ]
