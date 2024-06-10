from enum import StrEnum
from django.db import models
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex


class ProductStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"


class Product(models.Model):
    name = models.CharField(max_length=128)
    price = models.PositiveIntegerField()
    # is_active = models.BooleanField(default=False)
    status = models.CharField(max_length=8)  # active | inactive | paused
    category = models.ForeignKey("Category", on_delete=models.SET_NULL, null=True)
    tags = models.CharField(max_length=128, blank=True)
    search_vector = SearchVectorField(null=True)

    class Meta:
        app_label = "product"
        db_table = "product"
        indexes = [
            models.Index(fields=["status", "price"]),
            GinIndex(fields=["search_vector"]),
        ]


class Category(models.Model):
    name = models.CharField(max_length=32)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, related_name="children"
    )

    class Meta:
        app_label = "product"
        db_table = "category"
