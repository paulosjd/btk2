from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from rest_framework import serializers

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializers registration requests and creates a new user."""
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )
    email = serializers.CharField(
        max_length=50,
        validators=[validate_email]
    )
    token = serializers.CharField(
        max_length=255,
        read_only=True
    )

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'token']
        extra_kwargs = {'email': {'required': True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def validate_email(self, value):
        if User.objects.filter(email=value):
            raise serializers.ValidationError('Email is already registered')
        return value
