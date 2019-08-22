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
                    'available_unit_options']
    opt_fields = ['num_values'] + [f'value2_short_label_{i}' for i in [1, 2]]

    def get(self, request):
        profile = request.user.profile
        serializers = dict(zip(['profile_summary', 'all_params', 'datapoints'],
                               self.get_serializers(profile)))
        if all([ser.is_valid() for ser in serializers.values()]):
            resp_data = {k: v.data for k, v in serializers.items()}
            null_data_params = ProfileParamUnitOption.null_data_params(profile)
            resp_data.update({
                'date_formats': self.date_formats,
                'blank_params':
                    [{**{field: getattr(obj.parameter, field)
                         for field in self.param_fields},
                      **self.param_unit_opt_dct(obj.unit_option)}
                     for obj in null_data_params]
            })
            return Response(resp_data, status=status.HTTP_200_OK)
        return Response({'status': 'Bad request',
                         'errors': serializers['profile_summary'].errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def get_serializers(self, profile):
        summary_qs = profile.summary_data()
        sum_data = [{
            'parameter': {
                **{field: getattr(obj.parameter, field)
                   for field in self.param_fields[:3] + self.opt_fields[:3]},
                **self.param_unit_opt_dct(
                    ProfileParamUnitOption.get_unit_option(
                        profile, summary_qs[i].parameter)
                )},
            'data_point': {field: getattr(obj, field)
                           for field in ['date', 'value', 'value2']}}
            for i, obj in enumerate(summary_qs)]

        all_data = [{**{field: getattr(obj, field) for field in
                        ['id', 'date', 'value', 'value2', 'qualifier']},
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

    @staticmethod
    def param_unit_opt_dct(unit_opt):
        return {f'unit_{field}': getattr(unit_opt, field)
                for field in ['symbol', 'name', ]}
