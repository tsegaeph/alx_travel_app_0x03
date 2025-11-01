from rest_framework import serializers
from .models import TravelListing, Payment

class TravelListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelListing
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "booking", "transaction_id", "amount", "status", "created_at", "updated_at"]