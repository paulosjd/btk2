from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import Parameter, ProfileParamUnitOption
from app.serializers import (
    DataPointSerializer, ParameterSerializer, SummaryDataSerializer)


class ProfileSummaryData(APIView):
    date_formats = ['YYYY/MM/DD', 'YYYY-MM-DD', 'YY/MM/DD', 'YY-MM-DD',
                    'DD/MM/YYYY', 'DD-MM-YYYY', 'DD/MM/YY', 'DD-MM-YY']
    param_fields = ['name', 'upload_fields', 'upload_field_labels',
                    'default_unit_symbol', 'available_unit_options']

    def get(self, request):
        serializers = dict(zip(['profile_summary', 'all_params', 'datapoints'],
                               self.get_serializers(request.user.profile)))
        if all([ser.is_valid() for ser in serializers.values()]):
            resp_data = {k: v.data for k, v in serializers.items()}
            resp_data.update({
                'date_formats': self.date_formats,
                'blank_params':
                    [{field: getattr(obj.parameter, field)
                      for field in self.param_fields}
                     for obj in ProfileParamUnitOption.get_null_data_params(
                        request.user.profile)]
            })
            return Response(resp_data, status=status.HTTP_200_OK)
        return Response({'status': 'Bad request',
                         'errors': serializers['profile_summary'].errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def get_serializers(self, profile):
        summary_qs = profile.summary_data()

        def get_unit_of_measure_for_param(unit_opt):
            return {f'unit_{field}': getattr(unit_opt, field)
                    for field in ['symbol', 'name', ]}

        sum_data = [{
            'parameter': {
                **{field: getattr(obj.parameter, field)
                   for field in self.param_fields[:3]},
                **get_unit_of_measure_for_param(
                    ProfileParamUnitOption.get_unit_option(
                        profile, summary_qs[i].parameter)
                )},
            'data_point': {field: getattr(obj, field)
                           for field in ['date', 'value', 'value2']}}
            for i, obj in enumerate(summary_qs)]

        all_data = [{**{field: getattr(obj, field) for field in
                        ['id', 'date', 'value', 'value2']},
                     **{'parameter': obj.parameter.name,
                        'num_values': obj.parameter.num_values}}
                    for obj in profile.all_datapoints()]

        avail_params = [
            {field: getattr(obj, field) for field in self.param_fields}
            for obj in Parameter.objects.all()
        ]

        return (
            SummaryDataSerializer(data=sum_data, many=True),
            ParameterSerializer(data=avail_params, many=True),
            DataPointSerializer(data=all_data, many=True)
        )
