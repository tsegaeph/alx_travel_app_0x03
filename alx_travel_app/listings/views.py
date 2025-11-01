from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
import requests

from .tasks import send_booking_confirmation_email
from .models import TravelListing, Booking, Payment
from .serializers import TravelListingSerializer, BookingSerializer, PaymentSerializer


class TravelListingViewSet(viewsets.ModelViewSet):
    """
    Provides CRUD operations for TravelListing
    """
    queryset = TravelListing.objects.all()
    serializer_class = TravelListingSerializer


class BookingViewSet(viewsets.ModelViewSet):
    """
    Provides CRUD operations for Booking
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    @action(detail=True, methods=['post'])
    def initiate_payment(self, request, pk=None):
        """
        Initiates a payment for this booking using Chapa API
        """
        booking = self.get_object()
        amount = booking.total_price  # assuming your Booking model has total_price field
        currency = "ETB"  # adjust currency if needed

        chapa_api_key = settings.CHAPA_SECRET_KEY
        chapa_url = "https://api.chapa.co/v1/transaction/initialize"

        payload = {
            "amount": amount,
            "currency": currency,
            "tx_ref": f"booking_{booking.id}",
            "email": booking.user.email,  # assuming booking.user has email
            "first_name": booking.user.first_name,
            "last_name": booking.user.last_name,
            "callback_url": request.build_absolute_uri("/api/payments/verify/"),
        }

        headers = {
            "Authorization": f"Bearer {chapa_api_key}",
            "Content-Type": "application/json"
        }

        response = requests.post(chapa_url, json=payload, headers=headers)
        data = response.json()

        if response.status_code == 200 and data.get("status") == "success":
            # create Payment entry
            Payment.objects.create(
                booking=booking,
                transaction_id=data["data"]["tx_ref"],
                status="Pending",
                amount=amount
            )
            return Response(data, status=status.HTTP_200_OK)
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
    
    def perform_create(self, serializer):
        booking = serializer.save()
        # Trigger email asynchronously
        send_booking_confirmation_email.delay(booking.customer.email, booking.id)



class PaymentViewSet(viewsets.ViewSet):
    """
    Handles payment verification
    """

    @action(detail=False, methods=['post'])
    def verify(self, request):
        """
        Verify payment status from Chapa
        """
        tx_ref = request.data.get("tx_ref")
        if not tx_ref:
            return Response({"error": "tx_ref is required"}, status=status.HTTP_400_BAD_REQUEST)

        chapa_api_key = settings.CHAPA_SECRET_KEY
        verify_url = f"https://api.chapa.co/v1/transaction/verify/{tx_ref}"
        headers = {"Authorization": f"Bearer {chapa_api_key}"}

        response = requests.get(verify_url, headers=headers)
        data = response.json()

        try:
            payment = Payment.objects.get(transaction_id=tx_ref)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

        if response.status_code == 200 and data.get("status") == "success":
            payment.status = "Completed"
            payment.save()
            # Optionally: trigger a Celery task to send confirmation email
        else:
            payment.status = "Failed"
            payment.save()

        return Response(data)
    