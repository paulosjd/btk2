import logging

from rest_framework import status
from rest_framework.response import Response

from app.models import Bookmark
from .base import BaseBookmarksView

log = logging.getLogger(__name__)


class EditBookmarksView(BaseBookmarksView):

    def post(self, request):
        profile = request.user.profile
        if not profile:
            return Response({'error': 'Bad request'},
                            status=status.HTTP_400_BAD_REQUEST)

        form_data = request.data.get('value')
        print(form_data)
        # Bookmark.objects.create(
        #
        # )



        #
        #
        # parameter = Parameter.objects.custom_parameters().filter(
        #     name=form_data.get('parameter'), profile=profile).first()
        # if not parameter:
        #     parameter = Parameter.objects.filter(
        #         name=form_data.get('parameter')).first()
        #
        # if form_data and parameter:
        #     self.process_post_data(form_data, parameter)
        # else:
        #     log.debug('"form_data and parameter" condition unmet')
        # return self.json_response()

    # def process_post_data(self, form_data, parameter):
    #
    #     param_fields = parameter.upload_fields.split(', ')
    #     row_nums = set([k.split('_')[0] for k in form_data.keys()
    #                     if k and k.split('_')[0].isdigit()])
    #     for num in row_nums:
    #         try:
    #             dp_data = {field: form_data[f'{num}_{field}']
    #                        for field in param_fields + ['date']}
    #         except KeyError as e:
    #             log.error(e)
    #             print(e)
    #             continue
    #         for k, v in dp_data.items():
    #             try:
    #                 dp_data[k] = datetime.strptime(dp_data[k], '%Y-%m-%d') \
    #                     if k == 'date' else round(float(dp_data[k]), 2)
    #             except ValueError:
    #                 continue
    #         if not all(dp_data.values()):
    #             continue
    #
    #         DataPoint.update_on_date_match_or_create(
    #             parameter=parameter, profile=self.request.user.profile,
    #             **dp_data
    #         )
