from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db import connection
from products.models import Product
from orders.models import Order


@login_required
def dashboard(request):
    tenant = getattr(request, "tenant", None)
    storage = tenant.get_storage_usage() if tenant and hasattr(tenant, "get_storage_usage") else None

    context = {
        "schema": connection.schema_name,
        "products_count": Product.objects.count(),
        "orders_count": Order.objects.count(),
        "storage": storage,
    }
    return render(request, "accounts/dashboard.html", context)
