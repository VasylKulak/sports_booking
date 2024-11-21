from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User
from classes.models import Class
from bookings.models import Booking
from datetime import timedelta


class BaseTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser",
                                             email="testuser@example.com",
                                             password="password")
        self.other_user = User.objects.create_user(username="otheruser",
                                                   email="otheruser@example.com",
                                                   password="password")
        self.client.force_authenticate(user=self.user)

        self.sports_class = Class.objects.create(
            name="Yoga Class",
            date_time=timezone.now() + timedelta(hours=2),
            max_participants=10
        )


class BookingModelTest(BaseTestCase):
    def test_booking_str_representation(self):
        booking = Booking.objects.create(user=self.user,
                                         sports_class=self.sports_class)
        self.assertEqual(str(booking),
                         f"{self.user.username} booked {self.sports_class.name}")

    def test_booking_is_expired(self):
        booking = Booking.objects.create(user=self.user,
                                         sports_class=self.sports_class,
                                         created_at=timezone.now() - timedelta(
                                             minutes=16))
        self.assertTrue(booking.is_expired())

    def test_booking_can_book(self):
        valid_class = Class.objects.create(name="Valid Class",
                                           date_time=timezone.now() + timedelta(
                                               hours=3))
        expired_class = Class.objects.create(name="Expired Class",
                                             date_time=timezone.now() + timedelta(
                                                 minutes=30))
        valid_booking = Booking(user=self.user, sports_class=valid_class)
        expired_booking = Booking(user=self.user, sports_class=expired_class)
        self.assertTrue(valid_booking.can_book())
        self.assertFalse(expired_booking.can_book())


from bookings.serializers import BookingSerializer


class BookingSerializerTest(BaseTestCase):
    def test_validate_booking(self):
        data = {"sports_class": self.sports_class.id}
        serializer = BookingSerializer(data=data,
                                       context={"request": self.client})
        self.assertTrue(serializer.is_valid())

    def test_validate_booking_too_late(self):
        self.sports_class.date_time = timezone.now() + timedelta(minutes=30)
        self.sports_class.save()
        data = {"sports_class": self.sports_class.id}
        serializer = BookingSerializer(data=data,
                                       context={"request": self.client})
        self.assertFalse(serializer.is_valid())
        self.assertEqual(str(serializer.errors["non_field_errors"][0]),
                         "You can only book a class at least one hour in advance.")

    def test_validate_booking_already_booked(self):
        Booking.objects.create(user=self.user, sports_class=self.sports_class,
                               status=Booking.STATUS_PENDING)
        data = {"sports_class": self.sports_class.id}
        serializer = BookingSerializer(data=data,
                                       context={"request": self.client})
        self.assertFalse(serializer.is_valid())
        self.assertEqual(str(serializer.errors["non_field_errors"][0]),
                         "You have already booked this class.")


class BookingViewTest(BaseTestCase):
    def test_create_booking_successful(self):
        data = {"sports_class": self.sports_class.id}
        response = self.client.post("/bookings/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking.objects.count(), 1)
        booking = Booking.objects.first()
        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.status, Booking.STATUS_PENDING)

    def test_create_booking_fully_booked(self):
        self.sports_class.max_participants = 0
        self.sports_class.save()
        data = {"sports_class": self.sports_class.id}
        response = self.client.post("/bookings/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("This class is fully booked.",
                      response.data["non_field_errors"])

    def test_cancel_booking(self):
        booking = Booking.objects.create(user=self.user,
                                         sports_class=self.sports_class,
                                         status=Booking.STATUS_PENDING)
        response = self.client.delete(f"/bookings/{booking.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.STATUS_CANCELED)

    def test_cancel_booking_not_owner(self):
        booking = Booking.objects.create(user=self.other_user,
                                         sports_class=self.sports_class,
                                         status=Booking.STATUS_PENDING)
        response = self.client.delete(f"/bookings/{booking.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_confirm_attendance(self):
        booking = Booking.objects.create(user=self.user,
                                         sports_class=self.sports_class,
                                         status=Booking.STATUS_PENDING)
        data = {"booking_id": booking.id}
        response = self.client.post("/confirm-attendance/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.STATUS_CONFIRMED)
        self.assertIsNotNone(booking.confirmed_at)

    def test_confirm_attendance_not_owner(self):
        booking = Booking.objects.create(user=self.other_user,
                                         sports_class=self.sports_class,
                                         status=Booking.STATUS_PENDING)
        data = {"booking_id": booking.id}
        response = self.client.post("/confirm-attendance/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Booking not found.", response.data["non_field_errors"])
