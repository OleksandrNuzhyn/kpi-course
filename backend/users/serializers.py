from rest_framework import serializers
from .models import User


class CustomUserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk', 'email', 'first_name', 'last_name', 'middle_name', 'role')
        read_only_fields = ('pk', 'email', 'first_name', 'last_name', 'middle_name', 'role')