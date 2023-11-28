
from django.contrib import admin
import uuid
import json
from django import forms
from .models import Vendor,PurchaseOrder

class VendorAdminForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['name', 'contact_details', 'address']

class VendorAdmin(admin.ModelAdmin):
    form = VendorAdminForm
    list_display = ('vendor_code', 'name', 'contact_details', 'address', 'on_time_delivery_rate', 'quality_rating_avg', 'average_response_time', 'fulfillment_rate')
    search_fields = ('vendor_code', 'name')  

    readonly_fields = ('on_time_delivery_rate', 'quality_rating_avg', 'average_response_time', 'fulfillment_rate')  

    fieldsets = (
        ('Vendor Information', {
            'fields': ('name', 'contact_details', 'address'),
        }),
        ('Performance Metrics', {
            'fields': ('on_time_delivery_rate', 'quality_rating_avg', 'average_response_time', 'fulfillment_rate'),
            'classes': ('collapse',),  
        }),
    )

    def save_model(self, request, obj, form, change):
        # Auto-generate vendor_code 
        if not obj.vendor_code:
            vendor_name_prefix = obj.name[:3].upper()
            vendor_code_suffix = str(uuid.uuid4())[:5].upper()  
            obj.vendor_code = f"{vendor_name_prefix}-{vendor_code_suffix}"

        obj.calculate_performance_metrics()  
        super().save_model(request, obj, form, change)

class PurchaseOrderAdminForm(forms.ModelForm):

    items = forms.CharField(widget=forms.Textarea, required=False)
    
    class Meta:
        model = PurchaseOrder
        fields = ['vendor', 'order_date', 'delivery_date', 'items', 'quantity' ,'status' ,'quality_rating' ,'issue_date']

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Mark quality_rating and issue_date as optional
            self.fields['quality_rating'].required = False
            self.fields['issue_date'].required = False

        def clean_items(self):
        # Convert the input to JSON
            items = self.cleaned_data['items']
            try:
                return json.loads(items)
            except json.JSONDecodeError:
                # Handle the case where input is not valid JSON
                raise forms.ValidationError("Invalid JSON format for items")

class PurchaseOrderAdmin(admin.ModelAdmin):
    form = PurchaseOrderAdminForm
    list_display = ( 'po_number','vendor', 'order_date', 'delivery_date','items', 'quantity', 'status', 'quality_rating', 'issue_date','acknowledgment_date')
    search_fields = ('po_number', 'vendor__name')  
    list_filter = ('status', 'acknowledgment_date')  
    date_hierarchy = 'order_date'  

    fieldsets = (
        ('PurchaseOrder Information', {
            'fields': ('vendor', 'order_date', 'delivery_date','items', 'quantity', 'status', 'quality_rating', 'issue_date'),
        }),
     )

    readonly_fields = ('po_number', 'acknowledgment_date')  # Make po_number and acknowledgment_date read-only

    def save_model(self, request, obj, form, change):
        # Auto-generate po_number if not set
        if not obj.po_number:
            obj.po_number = str(uuid.uuid4())[:8].upper()  # Customize as needed

        if obj.status == 'Completed' and obj.quality_rating is not None:
            obj.quality_rating = round(obj.quality_rating, 2)  # Round to 2 decimal places

        # If acknowledgment_date is not set, set it to None
        if not obj.acknowledgment_date:
            obj.acknowledgment_date = None

        super().save_model(request, obj, form, change)

admin.site.register(Vendor, VendorAdmin)
admin.site.register(PurchaseOrder, PurchaseOrderAdmin)
