from django.db import models, transaction
from stores.models import Store
from catalog.models import Product
from audit.models import ReservationLog

ORDER_STATUS_CHOICES = (
    ('created', 'created'),
    ('awaiting_registration', 'awaiting_registration'),
    ('awaiting_delivery', 'awaiting_delivery'),
    ('cancelled', 'cancelled'),
)

class OrderStatusMap(models.Model):
    schema = models.CharField(max_length=16)
    ozon_status = models.CharField(max_length=64)
    internal_status = models.CharField(max_length=32, choices=ORDER_STATUS_CHOICES)

class Order(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    posting_number = models.CharField(max_length=255)
    base_order_number = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=32, choices=ORDER_STATUS_CHOICES)
    schema = models.CharField(max_length=8, default='FBS')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('store', 'posting_number')

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.IntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    expenses_allocated = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    markup_ratio_fact = models.DecimalField(max_digits=12, decimal_places=4, default=0)

@transaction.atomic
def set_order_status(order: Order, status_value: str):
    order = Order.objects.select_for_update().get(id=order.id)
    order.status = status_value
    order.save(update_fields=['status', 'updated_at'])
    for item in order.items.all():
        ReservationLog.objects.create(store_id=order.store_id, order_id=order.id, product_id=item.product_id, qty=item.qty, status=status_value)
    return order
