from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Train, Booking

class RegisterSerializer(serializers.ModelSerializer):
    model = User
    fields = ['username', 'password1', 'password2']
    extra_kwargs = {'password': {'write_only':True}}
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user