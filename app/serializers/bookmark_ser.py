from rest_framework import serializers

from app.models import Bookmark, Profile


class BookmarkSerializer(serializers.ModelSerializer):
    """ Serializer for Bookmark model """

    profile = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.all(),
        required=False,
        write_only=True
    )

    class Meta:
        model = Bookmark
        fields = ['url', 'title', 'param_name', 'profile']
