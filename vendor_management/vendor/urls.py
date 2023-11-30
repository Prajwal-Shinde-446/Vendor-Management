# urls.py
from django.urls import path
from .views import VendorListCreateView, VendorDetailView,PurchaseOrderListCreateView,PurchaseOrderDetailView,VendorPerformanceView,PurchaseOrderAcknowledgeView
from django.views.generic import RedirectView
print('hello')
urlpatterns = [
    path('', RedirectView.as_view(url='/admin/', permanent=True)),
    path('api/purchase_orders/<str:pk>/acknowledge/', PurchaseOrderAcknowledgeView.as_view(), name='purchaseorder-acknowledge'),
    path('api/vendors/', VendorListCreateView.as_view(), name='vendor-list-create'),
    path('api/vendors/<str:pk>/', VendorDetailView.as_view(), name='vendor-detail'),
    path('api/vendors/<str:vendor_code>/performance/', VendorPerformanceView.as_view(), name='vendor-performance'),
    path('api/purchase_orders/', PurchaseOrderListCreateView.as_view(), name='purchaseorder-list-create'),
    path('api/purchase_orders/<str:pk>/', PurchaseOrderDetailView.as_view(), name='purchaseorder-detail'),
   
]
