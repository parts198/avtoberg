from django.db import models

class ApiRequestLog(models.Model):
    method = models.CharField(max_length=10)
    url = models.CharField(max_length=255)
    request_body = models.TextField(blank=True)
    response_body = models.TextField(blank=True)
    status_code = models.IntegerField()
    duration_ms = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    store_id = models.IntegerField(null=True, blank=True)

class ApiErrorLog(models.Model):
    message = models.TextField()
    payload = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    store_id = models.IntegerField(null=True, blank=True)

class StockLog(models.Model):
    store_id = models.IntegerField()
    product_id = models.IntegerField()
    warehouse_id = models.IntegerField()
    delta = models.IntegerField()
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

class ReservationLog(models.Model):
    store_id = models.IntegerField()
    order_id = models.IntegerField()
    product_id = models.IntegerField()
    qty = models.IntegerField()
    status = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

class TaskLog(models.Model):
    command = models.CharField(max_length=64)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=32, default='started')
    message = models.TextField(blank=True)
