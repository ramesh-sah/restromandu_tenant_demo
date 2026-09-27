from django.urls import path
from .views import product_create, product_list

app_name = "products"
urlpatterns = [
    path("", product_list, name="list"),
    path("new/", product_create, name="create"),
]
