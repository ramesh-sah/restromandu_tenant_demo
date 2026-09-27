from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [("products", "0001_initial")]
    operations = [
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("number", models.CharField(max_length=30, unique=True)),
                ("quantity", models.PositiveIntegerField(default=1)),
                ("status", models.CharField(choices=[("OPEN", "Open"), ("PAID", "Paid"), ("CANCELLED", "Cancelled")], default="OPEN", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="products.product")),
            ],
            options={"ordering": ["-created_at"], "permissions": [("cancel_order", "Can cancel order"), ("print_order", "Can print order")]},
        ),
    ]
