from rest_framework import serializers

from app.models import Parameter


class ParameterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Parameter
        fields = ('name', 'upload_fields', 'upload_field_labels', 'default_unit_symbol', )
