from django.http import HttpResponseRedirect
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import Parameter, ProfileParamUnitOption, UnitOption
from app.serializers import ParameterSerializer
from app.utils.view_helpers import param_unit_opt_dct
from app.views.profile.summary_data import ProfileSummaryData


class CustomMetricAdd(APIView):
    serializer_class = ParameterSerializer

    def post(self, request):
        param_name = request.data.get('data', {}).get('param_name')
        unit_symbol = request.data.get('data', {}).get('unit_symbol')
        profile = request.user.profile
        if all([param_name, unit_symbol, profile]):
            pass




        # error_msg = 'Parameter or UnitOption lookup failed'
        # if unit_option and parameter:
        #     try:
        #         ProfileParamUnitOption.objects.get(
        #             parameter=parameter, profile=request.user.profile
        #         )
        #     except ProfileParamUnitOption.DoesNotExist:
        #         ProfileParamUnitOption.objects.create(
        #             parameter=parameter, profile=request.user.profile,
        #             unit_option=unit_option
        #         )
        #
        #     return HttpResponseRedirect(reverse('summary'))
        #
        # return Response({'error': error_msg},
        #                 status=status.HTTP_400_BAD_REQUEST)
