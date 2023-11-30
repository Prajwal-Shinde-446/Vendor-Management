from django.db.models.signals import Signal
from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import PurchaseOrder, Vendor

# Create a signal
purchase_order_updated = Signal()

@receiver(post_save, sender=PurchaseOrder)
def purchase_order_post_save(sender, instance, **kwargs):
    if instance.status == 'Completed':
        instance.vendor.calculate_performance_metrics_on_time_delivery()
        instance.vendor.save()

@receiver(post_save, sender=PurchaseOrder)
def purchase_order_updated_handler(sender, instance, **kwargs):
    # Check if the update is already in progress to avoid recursion
    if not hasattr(instance, '_updating_metrics'):
        instance._updating_metrics = True
        try:
            # Call the necessary logic to update metrics
            instance.vendor.calculate_performance_metrics()
            instance.vendor.save_with_performance_metrics()
        finally:
            # Reset the flag after the update
            del instance._updating_metrics


vendor_updated = Signal()

@receiver(post_save, sender=Vendor)
def vendor_updated_handler(sender, instance, **kwargs):
    # Check if the update is already in progress to avoid recursion
    if not hasattr(instance, '_updating_metrics'):
        instance._updating_metrics = True
        try:
            instance.save_with_performance_metrics()
        finally:
            # Reset the flag after the update
            del instance._updating_metrics