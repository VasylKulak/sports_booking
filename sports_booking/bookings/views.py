from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.core.mail import send_mail
from django.utils import timezone
from .models import Booking
from .serializers import BookingSerializer, ConfirmAttendanceSerializer
from rest_framework.permissions import IsAuthenticated

class BookingListCreateView(generics.ListCreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        booking = serializer.save(user=self.request.user)
        self.send_booking_confirmation_email(booking)

    def send_booking_confirmation_email(self, booking):
        """ Send email notification upon successful booking """
        subject = "Booking Confirmation"
        message = f"You have successfully booked the class: {booking.sports_class.name}"
        recipient_list = [booking.user.email]
        send_mail(subject, message, "noreply@example.com", recipient_list)

class BookingCancelView(generics.DestroyAPIView):
    queryset = Booking.objects.all()
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        booking = self.get_object()
        if booking.user != request.user:
            raise PermissionDenied("You do not have permission to cancel this booking.")
        booking.status = Booking.STATUS_CANCELED
        booking.save()
        return Response({"message": "Booking canceled successfully"}, status=status.HTTP_204_NO_CONTENT)

class ConfirmAttendanceView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ConfirmAttendanceSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            booking_id = serializer.validated_data['booking_id']
            try:
                booking = Booking.objects.get(id=booking_id, user=request.user)
                booking.status = Booking.STATUS_CONFIRMED
                booking.confirmed_at = timezone.now()
                booking.save()
                return Response({"message": "Attendance confirmed."}, status=status.HTTP_200_OK)
            except Booking.DoesNotExist:
                raise ValidationError("Booking not found.")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
