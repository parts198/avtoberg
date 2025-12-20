from rest_framework import serializers
from .models import PriceExpenseSnapshot, ExpensePolicySettings

class PriceExpenseSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceExpenseSnapshot
        fields = '__all__'

class ExpensePolicySettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpensePolicySettings
        fields = ['policy']
