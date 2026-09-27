from django.db import models
from products.models import Product

class Order(models.Model):
    STATUS_CHOICES = [("OPEN", "Open"), ("PAID", "Paid"), ("CANCELLED", "Cancelled")]
    number = models.CharField(max_length=30, unique=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="OPEN")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        permissions = [
            ("cancel_order", "Can cancel order"),
            ("print_order", "Can print order"),
        ]

    @property
    def total(self):
        return self.product.price * self.quantity
