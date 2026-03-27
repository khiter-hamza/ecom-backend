from rest_framework import serializers
from .models import StockMovement
from products.serializers import ProductVariantSerializer

class StockMovementSerializer(serializers.ModelSerializer):
    variant_details = ProductVariantSerializer(source='variant', read_only=True)
    performed_by_name = serializers.CharField(source='performed_by.email', read_only=True)

    class Meta:
        model = StockMovement
        fields = ['id', 'variant', 'variant_details', 'quantity', 'movement_type', 'reason', 'performed_by_name', 'created_at']
