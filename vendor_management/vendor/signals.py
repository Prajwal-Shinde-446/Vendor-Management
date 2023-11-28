from django.db.models.signals import Signal
from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import PurchaseOrder , Vendor

# Create a signal
purchase_order_updated = Signal()

@receiver(post_save, sender=PurchaseOrder)
def purchase_order_updated_handler(sender, instance, **kwargs):
    # Call the necessary logic to update metrics
    instance.vendor.calculate_performance_metrics()
    instance.vendor.save()


vendor_updated = Signal()

@receiver(post_save, sender=Vendor)
def vendor_updated_handler(sender, instance, **kwargs):
   
    instance.calculate_performance_metrics()
    instance.save()
  
    vendor_updated.send(sender=sender, instance=instance)
