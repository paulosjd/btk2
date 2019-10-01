from django.http import HttpResponseRedirect
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import Parameter, ProfileParamUnitOption, UnitOption
from app.serializers import ParameterSerializer


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

        return Response({'error': error_msg},
                        status=status.HTTP_400_BAD_REQUEST)
