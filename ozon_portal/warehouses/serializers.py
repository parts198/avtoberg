from rest_framework import serializers
from .models import Warehouse

class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ['id', 'name', 'external_id', 'type']

    def create(self, validated_data):
        store = self.context['request'].data.get('store') or self.context['request'].query_params.get('store')
        return Warehouse.objects.create(store_id=store, **validated_data)
