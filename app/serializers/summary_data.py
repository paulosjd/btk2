from rest_framework import serializers

from app.models import DataPoint
from .data_point import DataPointSerializer
from .parameter import ParameterSerializer


class SummaryDataPointSerializer(DataPointSerializer):
    class Meta:
        model = DataPoint
        exclude = ('profile', 'parameter')


class SummaryDataSerializer(serializers.Serializer):
    parameter = ParameterSerializer()
    data_point = SummaryDataPointSerializer()
    unit_name = serializers.CharField()
    unit_symbol = serializers.CharField()

    class Meta:
        fields = ('key', 'parameter', 'data_point', 'unit_name', 'unit_symbol')
