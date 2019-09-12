from rest_framework import serializers

from app.models import Parameter


class ParameterSerializer(serializers.ModelSerializer):
    available_unit_options = serializers.ListField(required=False)
    name = serializers.CharField()
    unit_name = serializers.CharField(required=False)
    unit_symbol = serializers.CharField(required=False)
    ideal_info = serializers.CharField(required=False, allow_blank=True)
    ideal_info_url = serializers.CharField(required=False, allow_blank=True)
    num_values = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Parameter
        fields = (
            'name', 'upload_fields', 'upload_field_labels',
            'available_unit_options', 'unit_name', 'unit_symbol',
            'num_values', 'ideal_info', 'ideal_info_url',
            *[f'value2_short_label_{i}' for i in [1, 2]]
        )
