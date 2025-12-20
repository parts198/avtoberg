from django.db import models
from django.contrib.auth.models import User
from stores.models import Store

class ProductGroup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_groups')
    name = models.CharField(max_length=255)
    confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products')
    offer_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255, blank=True)
    product_group = models.ForeignKey(ProductGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('store', 'offer_id')

    def __str__(self):
        return f"{self.offer_id} ({self.store.name})"

class OfferCandidate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    source_offer_id = models.CharField(max_length=255)
    target_offer_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
