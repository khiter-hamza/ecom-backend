from rest_framework import serializers
from django.db import transaction
from decimal import Decimal
from .models import Order, OrderItem
from products.models import ProductVariant

class OrderItemSerializer(serializers.ModelSerializer):
    variant_name = serializers.CharField(source='variant.__str__', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'variant', 'variant_name', 'quantity', 'price_at_purchase']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'order_id',
            'customer_name',
            'customer_phone',
            'wilaya',
            'commune',
            'shipping_address',
            'notes',
            'status',
            'delivery_price',
            'total_amount',
            'items',
            'created_at',
        ]

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError('Order must include at least one item.')
        return value

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        # Never trust client-provided status/total; backend computes these.
        validated_data['status'] = 'PENDING'

        delivery_price = Decimal(str(validated_data.get('delivery_price', Decimal('0.00'))))
        line_total = Decimal('0.00')

        with transaction.atomic():
            order = Order.objects.create(**validated_data)

            for item_data in items_data:
                variant = ProductVariant.objects.select_for_update().get(id=item_data['variant'].id)
                quantity = int(item_data.get('quantity', 0))
                if quantity < 1:
                    raise serializers.ValidationError({'items': 'Quantity must be at least 1.'})
                if variant.stock_quantity < quantity:
                    raise serializers.ValidationError(
                        {'items': f'Insufficient stock for variant {variant.sku}. Requested {quantity}, available {variant.stock_quantity}.'}
                    )

                unit_price = Decimal(str(variant.price))
                OrderItem.objects.create(
                    order=order,
                    variant=variant,
                    quantity=quantity,
                    price_at_purchase=unit_price,
                )
                line_total += unit_price * quantity

            order.total_amount = line_total + delivery_price
            order.save(update_fields=['total_amount'])

        return order
