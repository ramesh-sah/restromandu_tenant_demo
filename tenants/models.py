from django.db import models
from django.db import connection
from django_tenants.models import DomainMixin, TenantMixin

REFERENCE_SCHEMA = "_template"
DEFAULT_QUOTA_BYTES = 1 * 1024 * 1024 * 1024  # 1 GB


class Client(TenantMixin):
    name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    quota_bytes = models.BigIntegerField(
        default=DEFAULT_QUOTA_BYTES,
        help_text="Storage quota in bytes (default: 1 GB)",
    )

    auto_create_schema = False

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.schema_name})"

    def get_storage_usage(self):
        """
        Returns dict with storage metrics for this tenant schema:
        {
            'used_bytes': int,
            'quota_bytes': int,
            'used_pretty': str (e.g. "344 kB"),
            'quota_pretty': str (e.g. "1.00 GB"),
            'percent_used': float (e.g. 0.03),
            'is_over_quota': bool,
        }
        """
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT
                COALESCE(sum(pg_total_relation_size(quote_ident(table_schema) || '.' || quote_ident(table_name))), 0) AS raw_bytes,
                pg_size_pretty(COALESCE(sum(pg_total_relation_size(quote_ident(table_schema) || '.' || quote_ident(table_name))), 0)) AS pretty_size
            FROM information_schema.tables
            WHERE table_schema = %s;
            """,
            [self.schema_name],
        )
        row = cursor.fetchone()
        raw_bytes = int(row[0]) if row and row[0] else 0
        pretty_size = row[1] if row and row[1] else "0 bytes"

        percent = round((raw_bytes / self.quota_bytes) * 100, 2) if self.quota_bytes else 0
        quota_gb = round(self.quota_bytes / (1024 * 1024 * 1024), 2)

        return {
            "used_bytes": raw_bytes,
            "quota_bytes": self.quota_bytes,
            "used_pretty": pretty_size,
            "quota_pretty": f"{quota_gb} GB",
            "percent_used": percent,
            "is_over_quota": raw_bytes >= self.quota_bytes,
        }


class Domain(DomainMixin):
    pass
