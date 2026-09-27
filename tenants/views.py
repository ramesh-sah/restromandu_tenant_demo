import time
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import connection
from django_tenants.utils import tenant_context
from django_tenants.clone import CloneSchema
from .models import Client, Domain, REFERENCE_SCHEMA
from .forms import TenantCreateForm

_clone_fn_installed = False


def _ensure_clone_function():
    global _clone_fn_installed
    if not _clone_fn_installed:
        CloneSchema()._create_clone_schema_function()
        _clone_fn_installed = True


def _get_all_schema_usage():
    """
    Returns a dict mapping schema_name -> {
        'used_bytes': int,
        'used_pretty': str
    } for ALL schemas in 1 SQL query.
    """
    usage = {}
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT
                table_schema,
                COALESCE(sum(pg_total_relation_size(quote_ident(table_schema) || '.' || quote_ident(table_name))), 0) AS raw_bytes,
                pg_size_pretty(COALESCE(sum(pg_total_relation_size(quote_ident(table_schema) || '.' || quote_ident(table_name))), 0)) AS pretty_size
            FROM information_schema.tables
            WHERE table_schema NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
            GROUP BY table_schema;
        """)
        for schema, raw_bytes, pretty_size in cursor.fetchall():
            usage[schema] = {
                "used_bytes": int(raw_bytes),
                "used_pretty": pretty_size,
            }
    except Exception:
        pass
    return usage


def public_home(request):
    tenants = list(Client.objects.exclude(
        schema_name__in=["public", REFERENCE_SCHEMA],
    ))

    # Single query for primary domains
    domains = {
        d.tenant_id: d
        for d in Domain.objects.filter(tenant__in=tenants, is_primary=True)
    }

    # Single query for all schema storage usage
    all_usage = _get_all_schema_usage()

    for t in tenants:
        t.primary_domain = domains.get(t.id)
        u = all_usage.get(t.schema_name, {"used_bytes": 0, "used_pretty": "0 bytes"})
        t.used_bytes = u["used_bytes"]
        t.used_pretty = u["used_pretty"]
        t.quota_gb = round(t.quota_bytes / (1024 * 1024 * 1024), 2)
        t.percent_used = round((t.used_bytes / t.quota_bytes) * 100, 2) if t.quota_bytes else 0
        t.is_over_quota = t.used_bytes >= t.quota_bytes

    if request.method == "POST":
        form = TenantCreateForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            t0 = time.monotonic()

            tenant = Client(schema_name=cd["subdomain"], name=cd["restaurant_name"])
            tenant.save()

            _ensure_clone_function()
            cursor = connection.cursor()
            cursor.execute(
                "SELECT clone_schema(%(base)s, %(new)s, %(mode)s)",
                {"base": REFERENCE_SCHEMA, "new": cd["subdomain"], "mode": "NODATA"},
            )
            cursor.close()

            Domain.objects.create(
                domain=f"{cd['subdomain']}.localhost",
                tenant=tenant,
                is_primary=True,
            )

            with tenant_context(tenant):
                User.objects.create_superuser(
                    username=cd["admin_username"],
                    email=cd["admin_email"] or "",
                    password=cd["admin_password"],
                )

            elapsed = time.monotonic() - t0

            messages.success(
                request,
                f"Tenant '{cd['restaurant_name']}' created in {elapsed:.1f}s! "
                f"Access: http://{cd['subdomain']}.localhost:8000/ "
                f"(login: {cd['admin_username']})",
            )
            return redirect("public-home")
    else:
        form = TenantCreateForm()

    pub_usage = all_usage.get("public", {"used_bytes": 0, "used_pretty": "0 bytes"})

    return render(request, "tenants/public_home.html", {
        "form": form,
        "tenants": tenants,
        "public_storage": pub_usage["used_pretty"],
    })
