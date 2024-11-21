from rest_framework import generics, permissions, filters
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import Class
from .serializers import ClassSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated


class ClassListCreateView(generics.ListCreateAPIView):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['trainer', 'date_time']
    search_fields = ['name', 'description']
    permission_classes = [IsAuthenticated]


class ClassDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        if self.request.method in ['PUT', 'DELETE'] and obj.trainer != self.request.user:
            raise PermissionDenied("You do not have permission to modify this class.")
        return obj
