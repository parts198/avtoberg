from rest_framework import serializers
from .models import Product, ProductGroup, OfferCandidate

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'store', 'offer_id', 'name', 'product_group', 'created_at']
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {'store': {'write_only': True}}

class ProductGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductGroup
        fields = ['id', 'name', 'confirmed']

class OfferCandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferCandidate
        fields = ['id', 'source_offer_id', 'target_offer_id', 'approved']
