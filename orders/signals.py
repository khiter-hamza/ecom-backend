from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, OrderItem
from inventory.models import StockMovement

@receiver(post_save, sender=Order)
def handle_order_status_change(sender, instance, created, **kwargs):
    if created:
        print(f"NOTIFICATION: New Order from {instance.customer_name}!")

    # Reduce stock when order is CONFIRMED, SHIPPED or DELIVERED
    if instance.status in ['CONFIRMED', 'SHIPPED', 'DELIVERED']:
        for item in instance.items.all():
            # Standardized reason: specifically identifies a stock OUT for this order & item variant
            reason_str = f"Stock OUT for Order ID: {instance.order_id} | Variant: {item.variant.sku}"
            
            # Check if we ALREADY recorded an OUT movement for this specific order item
            if not StockMovement.objects.filter(variant=item.variant, movement_type='OUT', reason=reason_str).exists():
                StockMovement.objects.create(
                    variant=item.variant,
                    quantity=-item.quantity,
                    movement_type='OUT',
                    reason=reason_str
                )
    
    # Restore stock if order is CANCELLED
    elif instance.status == 'CANCELLED':
        for item in instance.items.all():
            reduction_reason = f"Stock OUT for Order ID: {instance.order_id} | Variant: {item.variant.sku}"
            return_reason = f"Stock RETURN (Cancelled Order): {instance.order_id}"
            
            # If we previously reduced stock, and haven't returned it yet
            if StockMovement.objects.filter(variant=item.variant, movement_type='OUT', reason=reduction_reason).exists() and \
               not StockMovement.objects.filter(variant=item.variant, movement_type='RET', reason=return_reason).exists():
                
                StockMovement.objects.create(
                    variant=item.variant,
                    quantity=item.quantity,
                    movement_type='RET',
                    reason=return_reason
                )


