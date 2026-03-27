import json
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from products.models import Category, Color, Size, Product, ProductVariant


class ProductMultipartCreateTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='creator@example.com', password='StrongPass123!')
        self.client.force_authenticate(user=self.user)

        self.category = Category.objects.create(name='Shirts')
        self.color = Color.objects.create(name='Black', hex_code='#000000')
        self.size = Size.objects.create(name='M')

    def test_create_product_with_variants_json_in_multipart(self):
        payload = {
            'name': 'Core Tee',
            'description': 'Premium cotton tee',
            'category': str(self.category.id),
            'is_active': 'true',
            'variants': json.dumps([
                {
                    'color': self.color.id,
                    'size': self.size.id,
                    'price': 49.99,
                    'stock_quantity': 12,
                }
            ]),
        }

        response = self.client.post('/api/products/', payload, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        product = Product.objects.get(id=response.data['id'])
        self.assertEqual(product.name, 'Core Tee')
        self.assertEqual(ProductVariant.objects.filter(product=product).count(), 1)
