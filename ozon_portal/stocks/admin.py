from django.contrib import admin
from .models import Stock, StockLock

admin.site.register(Stock)
admin.site.register(StockLock)
