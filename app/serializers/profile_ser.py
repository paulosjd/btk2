from rest_framework import serializers

from app.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """ Serializer for Profile model """

    class Meta:
        model = Profile
        fields = ['birth_year', 'gender', 'height']
