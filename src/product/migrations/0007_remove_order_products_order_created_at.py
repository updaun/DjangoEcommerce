# Generated by Django 5.0.1 on 2024-06-28 18:05

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("product", "0006_order_orderline_order_order_status_35c31c_idx"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="order",
            name="products",
        ),
        migrations.AddField(
            model_name="order",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
    ]
