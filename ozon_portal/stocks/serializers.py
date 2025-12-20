from rest_framework import serializers
from .models import Stock

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['id', 'product', 'warehouse', 'quantity', 'reserved', 'updated_at']

class StockUploadSerializer(serializers.Serializer):
    offer_id = serializers.CharField()
    warehouse = serializers.CharField()
    quantity = serializers.IntegerField()
