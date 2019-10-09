from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from .base import BaseBookmarksView
from app.models import Bookmark, Parameter


class AddBookmarksView(BaseBookmarksView):

    def post(self, request):
        self.profile = request.user.profile
        form_data = request.data.get('value', {})
        param_id, bm_url, bm_title = [form_data.get(s) for s in
                                      ['param_id', 'url', 'title']]
        data_is_valid = all([
            isinstance(param_id, int),
            bm_url and isinstance(bm_url, str) and len(bm_url) <= 100,
            bm_title and isinstance(bm_title, str) and len(bm_title) <= 50,
        ])
        if data_is_valid:
            parameter = get_object_or_404(Parameter.objects, id=param_id)
            Bookmark.objects.create(
                url=bm_url,
                title=bm_title,
                parameter=parameter,
                profile=self.profile
            )
            return self.json_response()
        return Response({'error': 'Bad request'},
                        status=status.HTTP_400_BAD_REQUEST)
