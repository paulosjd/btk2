# coding=utf-8
from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):
    pass
    # topics = TopicSerializer(many=True)
    #
    # class Meta:
    #     model = Category
    #     fields = ('name', 'logo', 'topics')

