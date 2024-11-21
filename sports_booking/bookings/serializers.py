from rest_framework import serializers
from .models import Booking
from classes.models import Class
from django.utils import timezone

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'user', 'sports_class', 'status', 'created_at', 'confirmed_at']
        read_only_fields = ['user', 'status', 'confirmed_at']

    def validate(self, attrs):
        user = self.context['request'].user
        sports_class = attrs.get('sports_class')

        # Check if booking is within the allowed timeframe (at least 1 hour before class starts)
        if (sports_class.date_time - timezone.now()).total_seconds() < 3600:
            raise serializers.ValidationError("You can only book a class at least one hour in advance.")

        # Check if the user has already booked the class
        if Booking.objects.filter(user=user, sports_class=sports_class).exists():
            raise serializers.ValidationError("You have already booked this class.")

        # Check if the class is full
        if sports_class.bookings.filter(status='confirmed').count() >= sports_class.max_participants:
            raise serializers.ValidationError("This class is fully booked.")
        return attrs


class ConfirmAttendanceSerializer(serializers.Serializer):
    booking_id = serializers.IntegerField()
