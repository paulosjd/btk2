from rest_framework import serializers

from app.models import Parameter


class ParameterSerializer(serializers.ModelSerializer):
    available_unit_options = serializers.ListField(required=False)
    name = serializers.CharField()
    unit_name = serializers.CharField(required=False)
    unit_symbol = serializers.CharField(required=False)

    class Meta:
        model = Parameter
        fields = (
            'name', 'upload_fields', 'upload_field_labels',
            'available_unit_options', 'unit_name', 'unit_symbol',
        )
