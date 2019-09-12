from django.http import HttpResponseRedirect
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import Parameter, ProfileParamUnitOption, UnitOption
from app.serializers import ParameterSerializer
from app.utils.view_helpers import param_unit_opt_dct
from app.views.profile.summary_data import ProfileSummaryData


class MenuItemAdd(APIView):
    serializer_class = ParameterSerializer

    def post(self, request):
        req_data = request.data.get('data', {})
        parameter = Parameter.objects.filter(
            name=req_data.get('param_choice')).first()
        unit_option = UnitOption.objects.filter(
            name=req_data.get('unit_choice')).first()
        error_msg = 'Parameter or UnitOption lookup failed'
        if unit_option and parameter:
            try:
                ProfileParamUnitOption.objects.get(
                    parameter=parameter, profile=request.user.profile
                )
            except ProfileParamUnitOption.DoesNotExist:
                ProfileParamUnitOption.objects.create(
                    parameter=parameter, profile=request.user.profile,
                    unit_option=unit_option
                )

            return HttpResponseRedirect(reverse('summary'))



            # param_fields = ['name', 'upload_fields', 'upload_field_labels',
            #                 'available_unit_options', 'num_values',
            #                 'ideal_info', 'ideal_info_url',
            #                 *[f'value2_short_label_{i}' for i in [1, 2]]]
            # mitm = {**{s: getattr(obj.parameter, s) for s in param_fields},
            #         **param_unit_opt_dct(obj.unit_option)}
            # return Response(mitm, status=status.HTTP_200_OK)

        return Response({'error': error_msg},
                        status=status.HTTP_400_BAD_REQUEST)
