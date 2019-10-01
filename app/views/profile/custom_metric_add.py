from django.http import HttpResponseRedirect
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import Parameter
from app.serializers import ParameterSerializer


class CustomMetricAdd(APIView):
    serializer_class = ParameterSerializer

    def post(self, request):
        param_name = request.data.get('data', {}).get('param_name')
        unit_symbol = request.data.get('data', {}).get('unit_symbol')
        profile = request.user.profile
        if all([param_name, unit_symbol, profile]):
            parameter, msg = Parameter.create_custom_metric(
                profile, param_name, unit_symbol
            )
            if parameter is False:
                return Response({'error': msg},
                                status=status.HTTP_400_BAD_REQUEST)

            return HttpResponseRedirect(reverse('summary'))
