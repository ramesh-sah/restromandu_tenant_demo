from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("accounts.urls")),
    path("products/", include("products.urls")),
    path("orders/", include("orders.urls")),
]
