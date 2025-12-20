from django.db import models
from catalog.models import Product
from django.contrib.auth.models import User

POLICY_CHOICES = (
    ('USE_MIN', 'Использовать минимум'),
    ('USE_MAX', 'Использовать максимум'),
)

class ExpensePolicySettings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    policy = models.CharField(max_length=16, choices=POLICY_CHOICES, default='USE_MAX')

class PriceExpenseSnapshot(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    marketing_seller_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    acquiring = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    commissions_percent_fbo = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    commissions_percent_fbs = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_ozon_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    markup_ratio = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    desired_marketing_seller_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    recalculated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product',)
