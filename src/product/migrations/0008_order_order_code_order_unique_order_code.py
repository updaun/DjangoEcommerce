# Generated by Django 5.0.1 on 2024-07-05 09:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("product", "0007_remove_order_products_order_created_at"),
        ("user", "0004_serviceuser_version"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="order_code",
            field=models.CharField(default="", max_length=32),
        ),
        migrations.AddConstraint(
            model_name="order",
            constraint=models.UniqueConstraint(
                fields=("order_code",), name="unique_order_code"
            ),
        ),
    ]
