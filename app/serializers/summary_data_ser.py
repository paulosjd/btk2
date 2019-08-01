from rest_framework import serializers

from app.models import DataPoint
from .parameter_ser import ParameterSerializer


class SummaryDataPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataPoint
        fields = ('value', 'value2', 'date', )


class SummaryDataSerializer(serializers.Serializer):
    parameter = ParameterSerializer()
    data_point = SummaryDataPointSerializer()

    class Meta:
        fields = ('key', 'parameter', 'data_point')
