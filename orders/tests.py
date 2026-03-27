from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from inventory.models import StockMovement
from products.models import Category, Color, Product, ProductVariant, Size


class OrderLifecycleFlowTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Jackets')
        self.color = Color.objects.create(name='Black', hex_code='#000000')
        self.size = Size.objects.create(name='M')
        self.product = Product.objects.create(
            name='Pro Softshell Jacket',
            description='Weather-ready professional jacket.',
            category=self.category,
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            color=self.color,
            size=self.size,
            price=Decimal('129.99'),
            stock_quantity=10,
        )

        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='StrongPass123!'
        )

    def _authenticate_admin(self):
        token_res = self.client.post(
            reverse('token_obtain_pair'),
            {'email': 'admin@example.com', 'password': 'StrongPass123!'},
            format='json',
        )
        self.assertEqual(token_res.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token_res.data['access']}")

    def test_user_to_admin_order_flow_reduces_stock_on_confirm(self):
        # 1) Customer places order (public endpoint)
        create_payload = {
            'customer_name': 'John Doe',
            'customer_phone': '+1-555-0100',
            'wilaya': 'Algiers',
            'commune': 'Bab El Oued',
            'shipping_address': '123 Commerce St',
            'notes': 'Please call before delivery',
            'delivery_price': '0.00',
            'items': [
                {
                    'variant': self.variant.id,
                    'quantity': 2,
                    'price_at_purchase': '129.99',
                }
            ]
        }
        create_res = self.client.post('/api/orders/', create_payload, format='json')
        self.assertEqual(create_res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create_res.data['status'], 'PENDING')
        self.assertEqual(create_res.data['wilaya'], 'Algiers')
        self.assertEqual(create_res.data['commune'], 'Bab El Oued')
        self.assertEqual(create_res.data['notes'], 'Please call before delivery')
        self.assertEqual(Decimal(str(create_res.data['total_amount'])), Decimal('259.98'))

        # 2) Admin confirms order via protected endpoint
        self._authenticate_admin()
        order_id = create_res.data['id']
        patch_res = self.client.patch(f'/api/orders/{order_id}/', {'status': 'CONFIRMED'}, format='json')
        self.assertEqual(patch_res.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_res.data['status'], 'CONFIRMED')

        # 3) Signal should create OUT stock movement and deduct stock
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock_quantity, 8)
        self.assertTrue(
            StockMovement.objects.filter(
                variant=self.variant,
                movement_type='OUT',
                quantity=-2,
            ).exists()
        )
