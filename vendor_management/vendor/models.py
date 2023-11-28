

from django.db import models
import uuid
from django.utils import timezone
from django.db.utils import OperationalError
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import  Avg, F, ExpressionWrapper, fields
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
            completed_pos = PurchaseOrder.objects.filter(
            vendor=self,
            status='Completed',
        )

            on_time_deliveries = completed_pos.filter(
            delivered_date__lte=F('delivery_date')
        )

            total_completed_pos = completed_pos.count()
            self.on_time_delivery_rate = (on_time_deliveries.count() / total_completed_pos) * 100 if total_completed_pos > 0 else 0.0
        except OperationalError as e:
            print(f"OperationalError in calculate_performance_metrics_on_time_delivery: {e}")
        except ObjectDoesNotExist as e:
            print(f"ObjectDoesNotExist in calculate_performance_metrics_on_time_delivery: {e}")

    def calculate_performance_metrics_quality_rating(self):
        try:
            completed_pos = self.purchaseorder_set.filter(status='Completed',vendor=self)

            self.quality_rating_avg = completed_pos.aggregate(Avg('quality_rating'))['quality_rating__avg'] or 0.0

        except OperationalError as e:
            print(f"OperationalError in calculate_performance_metrics_on_quality_rating: {e}")
        except ObjectDoesNotExist as e:
            print(f"ObjectDoesNotExist in calculate_performance_metrics_on_quality_rating: {e}")

    def calculate_performance_metrics_average_response_time(self):
        try:
            completed_pos = self.purchaseorder_set.filter(vendor=self,status='Completed')

            response_time_expr = ExpressionWrapper(
            F('acknowledgment_date') - F('issue_date'),
            output_field=fields.DurationField())
            self.average_response_time = completed_pos.annotate(response_time=response_time_expr).aggregate(Avg('response_time'))['response_time__avg'] or 0.0


        except OperationalError as e:
            print(f"OperationalError in calculate_performance_metrics_on_response_time: {e}")
        except ObjectDoesNotExist as e:
            print(f"ObjectDoesNotExist in calculate_performance_metrics_on_response_time: {e}")

    def calculate_performance_metrics_fulfilment_rate(self):
        try:
            all_pos = self.purchaseorder_set.all()
            completed_pos = all_pos.filter(vendor=self,status='Completed')

            self.fulfillment_rate = (completed_pos.count() / all_pos.count()) * 100 if all_pos.count() > 0 else 0.0

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

        try:
            self.clean_fields()  # Run built-in field validation
            self.calculate_performance_metrics()
        except ValidationError as e:
            # Handle validation errors
            print(f"Validation Error in save method: {e}")
        except Exception as e:
            print(f"Exception in calculate_performance_metrics: {e}")

        super().save(*args, **kwargs)
    
    


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
    quality_rating = models.FloatField(null=True, blank=True , validators=[MinValueValidator(0.0), MinValueValidator(5.0)])
    issue_date = models.DateTimeField(null=True, blank=True )
    acknowledgment_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.po_number:
            self.po_number = str(uuid.uuid4())[:8].upper()

        is_new = self._state.adding  # Check if the instance is being saved for the first time

        original_status = getattr(self._state, 'original', {}).get('status', None)

        if is_new or self.status != original_status:
            # If it's a new instance or the status has changed
            if self.status == 'Completed':
                # If the status is set to 'Completed', record the current date and time
                self.delivered_date = timezone.now()

        super().save(*args, **kwargs)
        if self.status == 'Completed':
            
            self.vendor.calculate_performance_metrics_on_time_delivery()
            self.vendor.calculate_performance_metrics_fulfilment_rate()

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