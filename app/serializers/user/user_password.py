from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework import serializers

User = get_user_model()


class UserPasswordSerializer(serializers.ModelSerializer):
    """ Validates password field and updates user if reset token is valid """

    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    class Meta:
        model = User
        fields = ['password']

    def save(self, token):
        token_generator = PasswordResetTokenGenerator()
        if token_generator.check_token(self.instance, token):
            self.instance.set_password(self.validated_data['password'])
            self.instance.save()
            return True
