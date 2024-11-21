from django.db import models
from users.models import User
from classes.models import Class
from django.utils import timezone

class Booking(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_CANCELED = 'canceled'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_CANCELED, 'Canceled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    sports_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='bookings')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} booked {self.sports_class.name}'

    def is_expired(self):
        """ Check if booking is older than 15 minutes and still pending """
        return self.status == self.STATUS_PENDING and (timezone.now() - self.created_at).total_seconds() > 900

    def can_book(self):
        """ Ensure booking is at least one hour before the class starts """
        return (self.sports_class.date_time - timezone.now()).total_seconds() > 3600
