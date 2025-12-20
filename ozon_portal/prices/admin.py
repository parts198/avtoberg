from django.contrib import admin
from .models import ExpensePolicySettings, PriceExpenseSnapshot

admin.site.register(ExpensePolicySettings)
admin.site.register(PriceExpenseSnapshot)
