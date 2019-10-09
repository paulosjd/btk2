import logging

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from app.models import Bookmark
from .base import BaseBookmarksView

log = logging.getLogger(__name__)


class EditBookmarksView(BaseBookmarksView):

    def post(self, request):
        self.profile = request.user.profile
        form_data = request.data.get('value', {})
        del_items = form_data.pop('delItems', [])
        param_id = form_data.pop('param_id', '')
        edit_data = {k: v for k, v in form_data.items() if isinstance(k, str)}
        obj_field_names = [s.split('_')[0] for s in edit_data.keys()]
        obj_field_value_ids = [s.split('_')[-1] for s in edit_data.keys()]
        obj_field_values = [v for v in edit_data.values()]
        data_is_valid = all([
            isinstance(param_id, int),
            isinstance(del_items, list),
            all([s.isdigit() for s in obj_field_value_ids]),
            len(obj_field_names) == len(obj_field_value_ids) == len(
                obj_field_values)
        ])
        if data_is_valid:
            for i, obj_id in enumerate(set(obj_field_value_ids)):
                obj = get_object_or_404(Bookmark.objects, id=obj_id)
                obj.title = obj_field_values[i * 2]
                obj.url = obj_field_values[i * 2 + 1]
                if int(obj_id) in del_items:
                    obj.delete()
                else:
                    obj.save()

            return self.json_response()

        return Response({'error': 'Bad request'},
                        status=status.HTTP_400_BAD_REQUEST)
