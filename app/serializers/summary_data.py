from rest_framework import serializers
from app.models import Profile


class SummaryDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        # fields = ('name', 'slug')