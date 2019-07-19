from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import Parameter, ProfileParamUnitOption
from app.serializers import ParameterSerializer, SummaryDataSerializer

import logging
log = logging.getLogger(__name__)


class ProfileSummaryData(APIView):
    date_formats = ['YYYY/MM/DD', 'YYYY-MM-DD', 'YY/MM/DD', 'YY-MM-DD', 'DD/MM/YYYY', 'DD-MM-YYYY', 'DD/MM/YY',
                    'DD-MM-YY']

    def get(self, request):

        queryset = request.user.profile.summary_data()
        summary_serializer, params_serializer = self.get_serializers(queryset, request.user.profile)

        if summary_serializer.is_valid() and params_serializer.is_valid():
            resp_data = {'profile_summary': summary_serializer.data,
                         'all_params': params_serializer.data,
                         'date_formats': self.date_formats}
            return Response(resp_data, status=status.HTTP_200_OK)

        log.error(f'SummaryDataSerializer instance errors ---> {summary_serializer.errors}', )
        if not params_serializer.is_valid():
            log.error(f'ParameterSerializer instance errors ---> {params_serializer.errors}', )
        return Response({'status': 'Bad request', 'errors': summary_serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_serializers(queryset, profile):

        data = [{'parameter': {field: getattr(obj.parameter, field) for field in
                               ['name', 'upload_fields', 'upload_field_labels']},
                 'data_point': {field: getattr(obj, field) for field in
                                ['date', 'time', 'value', 'value2']}}
                for obj in queryset]

        # Update each 'parameter' dict with units of measurement
        for ind, data_dct in enumerate(data):
            unit_option_record = ProfileParamUnitOption.get_unit_option(profile, queryset[ind].parameter)
            data_dct.update({f'unit_{field}': getattr(unit_option_record, field)
                             for field in ['symbol', 'name', ]})

        summary_serializer = SummaryDataSerializer(data=data, many=True)

        avail_params = [{field: getattr(obj, field) for field in ['name', 'upload_fields', 'upload_field_labels',
                                                                  'default_unit_symbol', 'available_unit_options']}
                        for obj in Parameter.objects.all()]
        params_serializer = ParameterSerializer(data=avail_params, many=True)

        return summary_serializer, params_serializer




