from django.contrib import admin
from django.urls import path
from tenants.views import public_home

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", public_home, name="public-home"),
]
