from rest_framework import serializers
from app.models import DataPoint


class DataPointSerializer(serializers.ModelSerializer):
    parameter = serializers.CharField(source='parameter.name')
    num_values = serializers.IntegerField(source='parameter.num_values',
                                          required=False)
    id = serializers.IntegerField(required=False)

    class Meta:
        model = DataPoint
        fields = ('id', 'value', 'value2', 'date', 'parameter', 'num_values')
