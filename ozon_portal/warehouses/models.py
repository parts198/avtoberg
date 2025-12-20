from django.db import models
from stores.models import Store

WAREHOUSE_TYPES = (
    ('FBO', 'FBO'),
    ('FBS', 'FBS'),
    ('rFBS', 'rFBS'),
)

class Warehouse(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='warehouses')
    name = models.CharField(max_length=255)
    external_id = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=WAREHOUSE_TYPES, default='FBS')

    class Meta:
        unique_together = ('store', 'external_id')

    def __str__(self):
        return f"{self.name} ({self.type})"
