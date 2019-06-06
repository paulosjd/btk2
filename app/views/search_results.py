# coding=utf-8
from rest_framework.generics import ListAPIView
from snippets.serializers import MarkdownSegmentSerializer
from snippets.models import MarkdownSegment


class TextSearchResultsView(ListAPIView):
    serializer_class = MarkdownSegmentSerializer
    queryset = MarkdownSegment.objects.all()
    text = ''

    def dispatch(self, request, *args, **kwargs):
        self.text = kwargs.get('text')
        return super(TextSearchResultsView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.queryset.filter(content__icontains=self.text).all()
