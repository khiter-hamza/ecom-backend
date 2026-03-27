from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Color, Size, Product, ProductVariant
from .serializers import (
    CategorySerializer, ColorSerializer, SizeSerializer, 
    ProductSerializer, ProductVariantSerializer
)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ColorViewSet(viewsets.ModelViewSet):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class SizeViewSet(viewsets.ModelViewSet):
    queryset = Size.objects.all()
    serializer_class = SizeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'variants__color', 'variants__size', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'variants__price']


class ProductVariantViewSet(viewsets.ModelViewSet):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
