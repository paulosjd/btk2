from rest_framework import serializers

from app.models import Bookmark


class BookmarkSerializer(serializers.ModelSerializer):
    """ Serializer for Bookmark model """

    class Meta:
        model = Bookmark
        fields = ['url', 'title', 'param_name', 'profile']
        extra_kwargs = {
            'param_name': {'write_only': True},
            'profile': {'write_only': True}
        }
