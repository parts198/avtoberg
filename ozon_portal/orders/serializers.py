from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'qty', 'price', 'revenue', 'expenses_allocated', 'markup_ratio_fact']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'posting_number', 'status', 'schema', 'items', 'created_at', 'updated_at']

class OrderStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['created','awaiting_registration','awaiting_delivery','cancelled'])
