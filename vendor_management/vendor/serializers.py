# vendor_management/serializers.py
from rest_framework import serializers
from .models import Vendor , PurchaseOrder

class VendorSerializer(serializers.ModelSerializer):
    vendor_code = serializers.CharField(read_only=True)
    class Meta:
        model = Vendor
        fields = '__all__'

class VendorPerformanceSerializer(serializers.Serializer):
    on_time_delivery_rate = serializers.FloatField()
    quality_rating_avg = serializers.FloatField()
    average_response_time = serializers.FloatField()
    fulfillment_rate = serializers.FloatField()


class PurchaseOrderSerializer(serializers.ModelSerializer):
    po_number = serializers.CharField(read_only=True)
    delivered_date = serializers.CharField(read_only=True)
    # quality_rating = serializers.CharField(read_only=True)
    acknowledgment_date = serializers.CharField(read_only=True)
    class Meta:
        model = PurchaseOrder
        fields = '__all__'


class PurchaseOrderAcknowledgeSerializer(serializers.Serializer):
    pass 