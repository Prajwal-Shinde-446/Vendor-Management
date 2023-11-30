

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
from datetime import timedelta
from django.utils import timezone
from django.db.utils import OperationalError,IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import  Avg, F, ExpressionWrapper, fields,FloatField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.text import slugify


class Vendor(models.Model):
    name = models.CharField(max_length=255)
    contact_details = models.TextField()
    address = models.TextField()
    vendor_code = models.CharField(max_length=50,primary_key=True, unique=True)
    on_time_delivery_rate = models.FloatField(default=0.0 , validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    quality_rating_avg = models.FloatField(default=0.0 , validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    average_response_time = models.FloatField(default=0.0 , validators=[MinValueValidator(0.0)])
    fulfillment_rate = models.FloatField(default=0.0 , validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])

    def __str__(self):
        return self.name
    

    
    

    def calculate_performance_metrics_on_time_delivery(self):
        try:
            print("rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr")
            completed_pos = PurchaseOrder.objects.filter(
            vendor=self,
            status='Completed',
        )
            print(completed_pos)

            on_time_deliveries = completed_pos.filter(
            delivered_date__lte=F('delivery_date')
        )
            print(on_time_deliveries)
            total_completed_pos = completed_pos.count()
            print(total_completed_pos)
            self.on_time_delivery_rate = (on_time_deliveries.count() / total_completed_pos) * 100 if total_completed_pos > 0 else 0.0
            print(self.on_time_delivery_rate)
            self.save()

        except OperationalError as e:
            print(f"OperationalError in calculate_performance_metrics_on_time_delivery: {e}")
        except ObjectDoesNotExist as e:
            print(f"ObjectDoesNotExist in calculate_performance_metrics_on_time_delivery: {e}")

    def calculate_performance_metrics_quality_rating(self):
        try:
            completed_pos = self.purchaseorder_set.filter(status='Completed', vendor=self)

            # Calculate the average quality rating
            avg_quality_rating = completed_pos.aggregate(Avg('quality_rating'))['quality_rating__avg'] or 0.0

            # Round the average to a reasonable number of decimal places
            rounded_avg_quality_rating = round(avg_quality_rating, 2)


            # Save the rounded average to the database
            self.quality_rating_avg = rounded_avg_quality_rating
            self.save(update_fields=['quality_rating_avg'])

        except OperationalError as e:
            print(f"OperationalError in calculate_performance_metrics_on_quality_rating: {e}")
        except ObjectDoesNotExist as e:
            print(f"ObjectDoesNotExist in calculate_performance_metrics_on_quality_rating: {e}")


    def calculate_performance_metrics_average_response_time(self):
        try:
            completed_pos = self.purchaseorder_set.filter(status='Completed').exclude(acknowledgment_date__isnull=True, issue_date__isnull=True)

            if completed_pos.exists():
                response_time_expr = ExpressionWrapper(
                    F('acknowledgment_date') - F('issue_date'),
                    output_field=fields.DurationField()
                )
                average_response_time = completed_pos.annotate(response_time=response_time_expr).aggregate(Avg('response_time'))['response_time__avg'] or timedelta(seconds=0)
                self.average_response_time = round(average_response_time.total_seconds(), 2)
                self.save()
            else:
                self.average_response_time = 0.0

        except OperationalError as e:
            print(f"OperationalError in calculate_performance_metrics_average_response_time: {e}")
        except ObjectDoesNotExist as e:
            print(f"ObjectDoesNotExist in calculate_performance_metrics_average_response_time: {e}")

    def calculate_performance_metrics_fulfilment_rate(self):
        try:
            all_pos = self.purchaseorder_set.all()
            completed_pos = all_pos.filter(vendor=self,status='Completed')

            self.fulfillment_rate = (completed_pos.count() / all_pos.count()) * 100 if all_pos.count() > 0 else 0.0
            self.save()

        except OperationalError as e:
            print(f"OperationalError in calculate_performance_metrics_fulfilment_rate: {e}")
        except ObjectDoesNotExist as e:
            print(f"ObjectDoesNotExist in calculate_performance_metrics_fulfilment_rate: {e}")


    def calculate_performance_metrics(self):
        # Common logic for overall metrics calculation
        self.calculate_performance_metrics_on_time_delivery()
        self.calculate_performance_metrics_quality_rating()
        self.calculate_performance_metrics_average_response_time()
        self.calculate_performance_metrics_fulfilment_rate()

    def save(self, *args, **kwargs):
        
        # Auto-generate vendor_code 
        if not self.vendor_code:
            vendor_name_prefix = self.name[:3].upper()
            vendor_code_suffix = str(uuid.uuid4())[:5].upper()  
            self.vendor_code = f"{vendor_name_prefix}-{vendor_code_suffix}"

        # Run built-in field validation before calculating metrics
        try:
            self.clean_fields()
        except ValidationError as e:
            # Handle validation errors
            raise  # Re-raise the exception to halt the save operation

        # Check if the instance is being created for the first time
        if not self.pk:
            try:
                # Calculate performance metrics only during creation, not during updates
                self.calculate_performance_metrics()
            except Exception as e:
                raise  # Re-raise the exception to halt the save operation

        # Save the model
        super().save(*args, **kwargs)
        print("Save successful")

    def save_with_performance_metrics(self, *args, **kwargs):
    # Save performance metrics first without triggering post_save signal
        super().save(*args, **kwargs)

        # Now calculate and save performance metrics again
        self.calculate_performance_metrics()
        super().save(update_fields=['on_time_delivery_rate'])
        super().save(update_fields=['quality_rating_avg'])

        super().save(*args, **kwargs)

# @receiver(post_save, sender=Vendor)
# def vendor_updated_handler(sender, instance, **kwargs):
#     # Disconnect the signal temporarily
#     post_save.disconnect(vendor_updated_handler, sender=sender)

#     try:
#         # Save the instance without triggering the signal
#         instance.save_base(raw=True)
#     except (OperationalError, IntegrityError, ValidationError) as e:
#         # Handle the exception, print a message, or log it
#         print(f"Error in vendor_updated_handler: {e}")
#     finally:
#         # Reconnect the signal after the save operation
#         post_save.connect(vendor_updated_handler, sender=sender)

# # Connect the signal after the model definition
# post_save.connect(vendor_updated_handler, sender=Vendor)
    
    


class PurchaseOrder(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    po_number = models.CharField(max_length=255,primary_key=True, unique=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    order_date = models.DateTimeField()
    delivery_date = models.DateTimeField()
    items = models.JSONField()
    delivered_date = models.DateTimeField(null=True, blank=True)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default='Pending')
    quality_rating = models.FloatField(null=True, blank=True , validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    issue_date = models.DateTimeField(null=True, blank=True )
    acknowledgment_date = models.DateTimeField(null=True, blank=True)

    def generate_unique_po_number(self):
        attempt_count = 0  # Limit the number of attempts to avoid an infinite loop
        while attempt_count < 5:  # You can adjust the number of attempts as needed
            new_po_number = str(uuid.uuid4())[:8].upper()
            if not PurchaseOrder.objects.filter(po_number=new_po_number).exists():
                print(f"Generated unique po_number: {new_po_number}")
                return new_po_number
            attempt_count += 1

        raise ValueError("Unable to generate a unique po_number after multiple attempts.")

    def save(self, *args, **kwargs):
        
        if not self.po_number:
            unique_po_number = self.generate_unique_po_number()
            self.po_number = unique_po_number

        is_new = self._state.adding  # Check if the instance is being saved for the first time
       

        original_status = getattr(self._state, 'original', {}).get('status', None)
        

        if is_new or self.status != original_status:
            # If it's a new instance or the status has changed
            if self.status == 'Completed':
                # If the status is set to 'Completed', record the current date and time
                self.delivered_date = timezone.now()
                self.vendor.calculate_performance_metrics_fulfilment_rate()
                self.vendor.calculate_performance_metrics_on_time_delivery()

        if self.status == 'Completed':
            self.vendor.calculate_performance_metrics_on_time_delivery()

        if self.quality_rating is not None:
            self.quality_rating = round(self.quality_rating, 2)
            self.vendor.calculate_performance_metrics_quality_rating()

        try:
            self.clean_fields()
        except ValidationError as e:
            print(f"Validation Error in save method: {e}")


        super().save(*args, **kwargs)
        
    


    class HistoricalPerformance(models.Model):
        vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
        date = models.DateTimeField()
        on_time_delivery_rate = models.FloatField()
        quality_rating_avg = models.FloatField()
        average_response_time = models.FloatField()
        fulfillment_rate = models.FloatField()