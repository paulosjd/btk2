import logging
from collections import namedtuple

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import ProfileParamUnitOption
from app.views.profile.summary_data import ProfileSummaryData

log = logging.getLogger(__name__)


class ParamColorsUpdateView(APIView):

    def get(self, request):
        return self.json_response(request.user.profile)

    def post(self, request):
        profile = request.user.profile
        param_names = set([k.split('_')[0] for k in request.data.keys()])
        name_obj_pairs = []
        for p_name in param_names:
            try:
                obj = ProfileParamUnitOption.objects.get(parameter__name=p_name,
                                                         profile=profile)
            except ProfileParamUnitOption.DoesNotExist as e:
                log.error(e)
                continue
            try:
                obj.color_hex = request.data[f'{p_name}_color_hex']
                obj.color_range_val_1 = request.data[f'{p_name}_min']
                obj.color_range_val_2 = request.data[f'{p_name}_max']
            except KeyError:
                return Response({'status': 'Bad request'},
                                status=status.HTTP_400_BAD_REQUEST)
            name_obj_pairs.append((p_name, obj))
        for name, obj in name_obj_pairs:
            obj.save()
        return self.json_response(name_obj_pairs)

    @staticmethod
    def json_response(name_obj_pairs):
        resp_data = []
        Item = namedtuple('ProfileParamObject',
                          ['param_name', 'pp_unit_option'])
        for name, obj in name_obj_pairs:
            item = Item(name, obj)
            resp_data.append(
                ProfileSummaryData.get_unit_info(item)
            )
        return Response(resp_data, status=status.HTTP_200_OK)
