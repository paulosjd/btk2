# coding=utf-8
from rest_framework.generics import ListAPIView
from snippets.serializers import MarkdownSegmentSerializer
from snippets.models import MarkdownSegment


class TopicSegmentsView(ListAPIView):
    serializer_class = MarkdownSegmentSerializer
    queryset = MarkdownSegment.objects.order_by('order').all()
    topic_name = ''

    def dispatch(self, request, *args, **kwargs):
        self.topic_name = kwargs.get('slug')
        return super(TopicSegmentsView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.queryset.filter(topic__slug=self.topic_name).order_by('order').all()
