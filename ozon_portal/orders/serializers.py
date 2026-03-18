from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    offer_id = serializers.CharField(source='product.offer_id', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'product',
            'product_id',
            'offer_id',
            'product_name',
            'qty',
            'price',
            'revenue',
            'expenses_allocated',
            'markup_ratio_fact',
        ]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'posting_number',
            'status',
            'schema',
            'store_name',
            'items',
            'created_at',
            'updated_at',
        ]

class OrderStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['created','awaiting_registration','awaiting_delivery','cancelled'])
