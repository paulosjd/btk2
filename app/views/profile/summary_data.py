from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import Parameter
from app.serializers import ParameterSerializer, SummaryDataSerializer

import logging
log = logging.getLogger(__name__)


class ProfileSummaryData(APIView):
    date_formats = ['YYYY/MM/DD', 'YYYY-MM-DD', 'YY/MM/DD', 'YY-MM-DD', 'DD/MM/YYYY', 'DD-MM-YYYY', 'DD/MM/YY',
                    'DD-MM-YY']

    def get(self, request):
        queryset = request.user.profile.summary_data()
        data = [{'parameter': {field: getattr(obj.parameter, field) for field in
                               ['name', 'upload_fields', 'upload_field_labels', 'default_unit_symbol']},
                 'data_point': {field: getattr(obj, field) for field in
                                ['date', 'time', 'value', 'value2']}}
                for obj in queryset]
        serializer = SummaryDataSerializer(data=data, many=True)

        avail_params = [{field: getattr(obj, field) for field in
                         ['name', 'upload_fields', 'upload_field_labels', 'default_unit_symbol']}
                        for obj in Parameter.objects.all()]
        params_serializer = ParameterSerializer(data=avail_params, many=True)

        if serializer.is_valid() and params_serializer.is_valid():
            resp_data = {'profile_summary': serializer.data,
                         'all_params': params_serializer.data,
                         'date_formats': self.date_formats}
            return Response(resp_data, status=status.HTTP_200_OK)

        log.error(f'SummaryDataSerializer instance errors ---> {serializer.errors}', )
        log.error(f'ParameterSerializer instance errors ---> {params_serializer.errors}', )
        return Response({'status': 'Bad request', 'errors': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def summary_data(self):
        pass



