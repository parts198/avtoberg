from django.db import models, transaction
from catalog.models import Product
from warehouses.models import Warehouse
from audit.models import StockLog

class StockLock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    locked_at = models.DateTimeField(auto_now_add=True)

class Stock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stocks')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    reserved = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'warehouse')

    @transaction.atomic
    def change(self, delta, reason='manual'):
        Stock.objects.select_for_update().get(id=self.id)
        self.quantity += delta
        self.save(update_fields=['quantity', 'updated_at'])
        StockLog.objects.create(store_id=self.product.store_id, product_id=self.product_id, warehouse_id=self.warehouse_id, delta=delta, reason=reason)
