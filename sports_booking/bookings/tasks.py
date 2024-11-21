from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from .models import Booking

@shared_task
def auto_cancel_bookings():
    """ Auto-cancel bookings that remain unconfirmed after 15 minutes """
    expired_bookings = Booking.objects.filter(status='pending')
    for booking in expired_bookings:
        if booking.is_expired():
            booking.status = 'canceled'
            booking.save()

@shared_task
def send_class_reminders():
    """ Send email reminders for upcoming classes scheduled within the next 24 hours """
    upcoming_bookings = Booking.objects.filter(
        status='confirmed',
        sports_class__date_time__range=(timezone.now(), timezone.now() + timezone.timedelta(hours=24))
    )

    for booking in upcoming_bookings:
        send_mail(
            "Class Reminder",
            f"Reminder: Your class '{booking.sports_class.name}' is scheduled within the next 24 hours.",
            "noreply@example.com",
            [booking.user.email],
            fail_silently=True,
        )
