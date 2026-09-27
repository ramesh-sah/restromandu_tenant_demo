from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import redirect, render
from .models import Product

@login_required
def product_list(request):
    return render(request, "products/list.html", {"products": Product.objects.all()})

@login_required
@permission_required("products.add_product", raise_exception=True)
def product_create(request):
    if request.method == "POST":
        Product.objects.create(name=request.POST["name"], price=request.POST["price"])
        return redirect("products:list")
    return render(request, "products/form.html")
