from enum import StrEnum
from django.db import models


class ProductStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"


class Product(models.Model):
    name = models.CharField(max_length=128)
    price = models.PositiveIntegerField()
    # is_active = models.BooleanField(default=False)
    status = models.CharField(max_length=8)  # active | inactive | paused

    class Meta:
        app_label = "product"
        db_table = "product"
        indexes = [
            models.Index(fields=["status", "price"]),
        ]
