from django.urls import path
from .views import cancel_order, order_list

app_name = "orders"
urlpatterns = [
    path("", order_list, name="list"),
    path("<int:pk>/cancel/", cancel_order, name="cancel"),
]
