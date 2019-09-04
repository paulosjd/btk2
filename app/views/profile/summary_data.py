from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import Parameter, ProfileParamUnitOption
from app.serializers import (
    DataPointSerializer, ParameterSerializer, SummaryDataSerializer)
from app.utils.calc_param_ideal import CalcParamIdeal


class ProfileSummaryData(APIView):
    date_formats = ['YYYY/MM/DD', 'YYYY-MM-DD', 'YY/MM/DD', 'YY-MM-DD',
                    'DD/MM/YYYY', 'DD-MM-YYYY', 'DD/MM/YY', 'DD-MM-YYround']
    param_fields = ['name', 'upload_fields', 'upload_field_labels',
                    'ideal_info', 'available_unit_options', ]
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
                     for obj in null_data_params],
            })
            self.update_with_ideals_data(resp_data, profile)
            return Response(resp_data, status=status.HTTP_200_OK)
        return Response({'status': 'Bad request',
                         'errors': serializers['profile_summary'].errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def get_serializers(self, profile):
        summary_qs = profile.summary_data()
        sum_data = [{
            'parameter': {
                **{field: getattr(obj.parameter, field)
                   for field in self.param_fields[:4] + self.opt_fields[:3]},
                **self.param_unit_opt_dct(
                    ProfileParamUnitOption.get_unit_option(
                        profile, summary_qs[i].parameter)
                )},
            'data_point': {field: getattr(obj, field)
                           for field in ['date', 'value', 'value2']},
        } for i, obj in enumerate(summary_qs)]

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

    @staticmethod
    def update_with_ideals_data(resp_data, profile):
        resp_data['ideals'] = []
        for obj in resp_data['profile_summary']:
            param_name = obj['parameter']['name']
            try:
                profile_param = ProfileParamUnitOption.objects.get(
                    parameter__name=param_name, profile=profile
                )
            except ProfileParamUnitOption.DoesNotExist:
                param_ideal = CalcParamIdeal(param_name, profile)
                target_data = {'saved': None,
                               'ideal': param_ideal.get_ideal(),
                               'misc_info': param_ideal.misc_data}
            else:
                target_obj = profile_param.targets(
                    obj['data_point']['value']
                )
                target_data = {'saved': target_obj.saved,
                               'ideal': target_obj.ideal,
                               'misc_info': target_obj.misc_data}
            resp_data['ideals'].append(target_data)
