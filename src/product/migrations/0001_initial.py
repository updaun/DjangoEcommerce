# Generated by Django 5.0.1 on 2024-06-09 14:27

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=128)),
                ("price", models.PositiveIntegerField()),
                ("status", models.CharField(max_length=8)),
            ],
            options={
                "db_table": "product",
                "indexes": [
                    models.Index(
                        fields=["status", "price"], name="product_status_43cca2_idx"
                    )
                ],
            },
        ),
    ]
