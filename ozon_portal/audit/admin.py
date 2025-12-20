from django.contrib import admin
from .models import ApiRequestLog, ApiErrorLog, StockLog, ReservationLog, TaskLog

admin.site.register(ApiRequestLog)
admin.site.register(ApiErrorLog)
admin.site.register(StockLog)
admin.site.register(ReservationLog)
admin.site.register(TaskLog)
