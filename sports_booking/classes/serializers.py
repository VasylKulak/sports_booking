from rest_framework import serializers
from .models import Class

class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ['id', 'name', 'description', 'date_time', 'duration', 'max_participants', 'trainer']
        read_only_fields = ['trainer']
