from rest_framework import generics
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from .models import Vendor,PurchaseOrder
from .serializers import VendorSerializer,PurchaseOrderSerializer,VendorPerformanceSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

#function for generating auth Token
class ObtainAuthTokenView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        else:
            return Response({'error': 'Invalid credentials'}, status=400)

#function to create a vendor and list display
class VendorListCreateView(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer

    def perform_create(self, serializer):
        # Call the parent perform_create to save the instance
        instance = serializer.save()

        try:
            instance.calculate_performance_metrics()
        except Exception as e:
            print(f"Exception in calculate_performance_metrics: {e}")

        instance.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

#Get a vendors details and update or delete a vendor
class VendorDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer

#Get performance metrices
class VendorPerformanceView(generics.RetrieveAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Vendor.objects.all()
    serializer_class = VendorPerformanceSerializer
    lookup_field = 'vendor_code'



#function to create a PurchaseOrder and list display
class PurchaseOrderListCreateView(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = PurchaseOrderSerializer

    def get_queryset(self):
        vendor_code = self.request.query_params.get('vendor_code')
        if vendor_code:
            return PurchaseOrder.objects.filter(vendor_code=vendor_code)
        return PurchaseOrder.objects.all()

    def perform_create(self, serializer):
        serializer.save(status='Pending', acknowledgment_date=None)

#Get a PurchaseOrder details and update or delete a vendor
class PurchaseOrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer

    
#class function to acknowledge the PurchaseOrder
@method_decorator(csrf_exempt, name='dispatch')   
class PurchaseOrderAcknowledgeView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    print("yooooooooooo")
    def post(self, request, pk):
        print("okayyyyyyy")
        purchase_order = self.get_object(pk)
        
        # Check if the vendor making the request is the owner of the purchase order , Since there is no actaul vendor this part is commented
        # if request.user != purchase_order.vendor.user:
        #     return Response({"detail": "You do not have permission to acknowledge this order."}, status=status.HTTP_403_FORBIDDEN)

        purchase_order.acknowledgment_date = timezone.now()
        purchase_order.save()

        # Assuming you have a related name for the PurchaseOrder vendor field in your Vendor model
        purchase_order.vendor.calculate_performance_metrics_average_response_time()

        return Response({"detail": "Order acknowledged successfully."}, status=status.HTTP_200_OK)

    def get_object(self, pk):
        # Use get_object_or_404 for simplicity
        return get_object_or_404(PurchaseOrder, pk=pk)

    

