from django.urls import path
from .views import BookingListCreateView, BookingCancelView, ConfirmAttendanceView

urlpatterns = [
    path('', BookingListCreateView.as_view(), name='booking-list-create'),
    path('<int:pk>/cancel/', BookingCancelView.as_view(), name='booking-cancel'),
    path('confirm-attendance/', ConfirmAttendanceView.as_view(), name='confirm-attendance'),
]
