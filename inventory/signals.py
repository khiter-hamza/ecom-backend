from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import StockMovement

@receiver(post_save, sender=StockMovement)
def update_variant_stock(sender, instance, created, **kwargs):
    if created:
        variant = instance.variant
        variant.stock_quantity += instance.quantity
        variant.save()
