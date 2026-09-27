"""
Ensure the reference/template schema exists and is fully migrated.
Run after makemigrations / before deploying new code.

    python manage.py ensure_template_schema
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from tenants.models import Client, REFERENCE_SCHEMA


class Command(BaseCommand):
    help = "Create or migrate the reference template schema used for fast tenant cloning."

    def handle(self, *args, **options):
        tenant, created = Client.objects.get_or_create(
            schema_name=REFERENCE_SCHEMA,
            defaults={"name": "Template (do not use)"},
        )
        if created:
            # Need to create schema + run migrations
            from django.db import connection
            connection.set_schema_to_public()
            call_command("migrate_schemas", schema_name=REFERENCE_SCHEMA, verbosity=1)
            self.stdout.write(self.style.SUCCESS(f"Created and migrated {REFERENCE_SCHEMA}"))
        else:
            call_command("migrate_schemas", schema_name=REFERENCE_SCHEMA, verbosity=1)
            self.stdout.write(self.style.SUCCESS(f"Migrated {REFERENCE_SCHEMA}"))
