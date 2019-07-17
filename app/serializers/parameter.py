from rest_framework import serializers

from app.models import Parameter


class ParameterSerializer(serializers.ModelSerializer):
    available_unit_options = serializers.ListField(required=False)
    name = serializers.CharField()

    class Meta:
        model = Parameter
        fields = ('name', 'upload_fields', 'upload_field_labels', 'available_unit_options')
