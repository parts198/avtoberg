from rest_framework import serializers
from .models import ApiRequestLog, ApiErrorLog, StockLog, ReservationLog, TaskLog

class ApiRequestLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiRequestLog
        fields = '__all__'

class ApiErrorLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiErrorLog
        fields = '__all__'

class StockLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockLog
        fields = '__all__'

class ReservationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservationLog
        fields = '__all__'

class TaskLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskLog
        fields = '__all__'
