# coding=utf-8
from rest_framework.generics import ListAPIView

from snippets.models import Category
from snippets.serializers import CategorySerializer


class CategoriesListView(ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.order_by('name').all()
