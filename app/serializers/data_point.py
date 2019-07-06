from rest_framework import serializers
from app.models import DataPoint


class DataPointSerializer(serializers.ModelSerializer):

    class Meta:
        model = DataPoint
        fields = ('value', 'value2', 'date', 'time', 'parameter', 'profile')
