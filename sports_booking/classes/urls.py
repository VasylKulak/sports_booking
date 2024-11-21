from django.urls import path
from .views import ClassListCreateView, ClassDetailView

urlpatterns = [
    path('', ClassListCreateView.as_view(), name='class-list-create'),
    path('<int:pk>/', ClassDetailView.as_view(), name='class-detail'),
]
