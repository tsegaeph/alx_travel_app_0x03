from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TravelListingViewSet, BookingViewSet, PaymentViewSet

# Create the default router
router = DefaultRouter()
router.register(r'travel-listings', TravelListingViewSet, basename='travellisting')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'payments', PaymentViewSet, basename='payment')  # added PaymentViewSet

# Include all router URLs under /api/
urlpatterns = [
    path('api/', include(router.urls)),
]
