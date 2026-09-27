from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from .models import Order

@login_required
def order_list(request):
    return render(request, "orders/list.html", {"orders": Order.objects.select_related("product")})

@login_required
@permission_required("orders.cancel_order", raise_exception=True)
def cancel_order(request, pk):
    if request.method == "POST":
        Order.objects.filter(pk=pk).update(status="CANCELLED")
    return render(request, "orders/list.html", {"orders": Order.objects.select_related("product")})
