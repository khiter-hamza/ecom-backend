from django.db import models
from products.models import ProductVariant
import uuid

class Order(models.Model):
    ORDER_STATUS = (
        ('PENDING', 'Pending (New Lead)'),
        ('CONFIRMED', 'Confirmed (Call Made)'),
        ('SHIPPED', 'In Transit'),
        ('DELIVERED', 'Delivered (Complete)'),
        ('CANCELLED', 'Order Cancelled'),
    )

    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    customer_name = models.CharField(max_length=255)
    customer_phone = models.CharField(max_length=25)
    wilaya = models.CharField(max_length=120, blank=True, default='')
    commune = models.CharField(max_length=120, blank=True, default='')
    shipping_address = models.TextField()
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='PENDING')
    delivery_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.order_id} | {self.customer_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, related_name='order_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2) # Locked price

    def __str__(self):
        return f"{self.quantity} x {self.variant} @ {self.price_at_purchase}"
