from rest_framework import serializers
import json
from .models import Category, Color, Size, Product, ProductVariant, ProductImage

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = '__all__'

class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = '__all__'

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'

class ProductVariantSerializer(serializers.ModelSerializer):
    color_name = serializers.CharField(source='color.name', read_only=True)
    size_name = serializers.CharField(source='size.name', read_only=True)

    class Meta:
        model = ProductVariant
        fields = ['id', 'color', 'size', 'color_name', 'size_name', 'price', 'discount_price', 'stock_quantity', 'sku']

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    variants = ProductVariantSerializer(many=True) # Now writeable
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description', 'category', 'category_name', 'thumbnail', 'variants', 'images', 'is_active']

    def to_internal_value(self, data):
        # Handle variants sent as JSON string in multipart/form-data.
        # QueryDict does not reliably preserve nested structures after direct assignment,
        # so normalize to a plain dict before passing to DRF internals.
        normalized_data = data
        if hasattr(data, 'dict'):
            normalized_data = data.dict()

        raw_variants = normalized_data.get('variants') if isinstance(normalized_data, dict) else None
        if isinstance(raw_variants, str):
            try:
                normalized_data['variants'] = json.loads(raw_variants)
            except (json.JSONDecodeError, ValueError):
                raise serializers.ValidationError({'variants': 'Invalid JSON payload for variants.'})

        return super().to_internal_value(normalized_data)

    def create(self, validated_data):
        variants_data = validated_data.pop('variants', [])
        product = Product.objects.create(**validated_data)
        for variant_data in variants_data:
            ProductVariant.objects.create(product=product, **variant_data)
        return product

    def update(self, instance, validated_data):
        variants_data = validated_data.pop('variants', [])
        
        # Update product fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update/Create variants
        keep_variant_ids = []
        for variant_data in variants_data:
            variant_id = variant_data.get('id')
            if variant_id:
                variant = ProductVariant.objects.get(id=variant_id, product=instance)
                for attr, value in variant_data.items():
                    setattr(variant, attr, value)
                variant.save()
                keep_variant_ids.append(variant.id)
            else:
                new_variant = ProductVariant.objects.create(product=instance, **variant_data)
                keep_variant_ids.append(new_variant.id)
        
        # Remove variants that are not in the payload
        ProductVariant.objects.filter(product=instance).exclude(id__in=keep_variant_ids).delete()
        
        return instance
