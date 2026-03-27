from django.db import models
from products.models import ProductVariant
from django.conf import settings

class StockMovement(models.Model):
    MOVEMENT_TYPES = (
        ('IN', 'Stock Received'),
        ('OUT', 'Stock Dispatched (Order)'),
        ('ADJ', 'Manual Adjustment'),
        ('RET', 'Customer Return'),
    )

    variant = models.ForeignKey(ProductVariant, related_name='movements', on_delete=models.CASCADE)
    quantity = models.IntegerField() # Positive for IN, Negative for OUT
    movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPES)
    reason = models.TextField(blank=True)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.movement_type} | {self.variant} | {self.quantity}"
