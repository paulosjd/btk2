from collections import namedtuple

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import Parameter, ProfileParamUnitOption
from app.serializers import (
    DataPointSerializer, ParameterSerializer, SummaryDataSerializer)
from app.utils.calc_param_ideal import CalcParamIdeal
from app.utils.view_helpers import get_summary_data, param_unit_opt_dct


class ProfileSummaryData(APIView):
    date_formats = ['YYYY/MM/DD', 'YYYY-MM-DD', 'YY/MM/DD', 'YY-MM-DD',
                    'DD/MM/YYYY', 'DD-MM-YYYY', 'DD/MM/YY', 'DD-MM-YY']
    param_fields = ['name', 'upload_fields', 'upload_field_labels',
                    'num_values', 'ideal_info', 'ideal_info_url',
                    'available_unit_options', ]
    opt_fields = ['num_values'] + [f'value2_short_label_{i}' for i in [1, 2]]
    profile_params = []

    def get(self, request):
        profile = request.user.profile
        serializers = dict(zip(['profile_summary', 'all_params', 'datapoints'],
                               self.get_serializers(profile)))
        if all([ser.is_valid() for ser in serializers.values()]):
            resp_data = {k: v.data for k, v in serializers.items()}
            null_data_params = ProfileParamUnitOption.null_data_params(profile)

            non_blank_param_names = [a.get('parameter', {}).get('name', '')
                                     for a in resp_data['profile_summary']]
            print(non_blank_param_names)
            print([a.parameter.name for a in null_data_params])

            resp_data.update({
                'date_formats': self.date_formats,
                'blank_params':
                    [{**{field: getattr(obj.parameter, field)
                         for field in self.param_fields},
                      **param_unit_opt_dct(obj.unit_option)}
                     for obj in null_data_params],
            })
            self.update_with_ideals_data(resp_data, profile)
            self.update_with_units_options(resp_data)
            return Response(resp_data, status=status.HTTP_200_OK)
        return Response({'status': 'Bad request',
                         'errors': serializers['profile_summary'].errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def get_serializers(self, profile):
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
            SummaryDataSerializer(data=get_summary_data(profile), many=True),
            ParameterSerializer(data=avail_params, many=True),
            DataPointSerializer(data=all_data, many=True)
        )

    def update_with_ideals_data(self, resp_data, profile):
        resp_data['ideals'] = []
        ProfileParamObj = namedtuple('profile_param_obj',
                                     ['param_name', 'pp_unit_option'])

        Item = namedtuple('UnitOptLookupData', ['param_name', 'value'])
        profile_summary_items = [Item(obj['parameter']['name'],
                                      obj['data_point']['value'])
                                 for obj in resp_data['profile_summary']]
        blank_param_items = [Item(obj['name'], None)
                             for obj in resp_data['blank_params']]
        profile_params = profile_summary_items + blank_param_items
        for obj in profile_params:
            print(obj.param_name)

        for obj in profile_params:
            try:
                profile_param = ProfileParamUnitOption.objects.get(
                    parameter__name=obj.param_name, profile=profile
                )
            except ProfileParamUnitOption.DoesNotExist:
                profile_param = None
                param_ideal = CalcParamIdeal(obj.param_name, profile)
                ideal_val = param_ideal.get_ideal()
                target_data = {'saved': None,
                               'saved2': None,
                               'ideal': ideal_val,
                               'missing_field': param_ideal.required_field,
                               'misc_info': param_ideal.misc_data}
            else:
                target_obj = profile_param.targets(obj.value)
                target_data = {'saved': target_obj.saved,
                               'saved2': target_obj.saved2,
                               'ideal': target_obj.ideal,
                               'missing_field': target_obj.required_field,
                               'misc_info': target_obj.misc_data}

            resp_data['ideals'].append(target_data)
            self.profile_params.append(
                ProfileParamObj(obj.param_name, profile_param)
            )

    def update_with_units_options(self, resp_data):
        resp_data['unit_info'] = []
        added_item_names = []
        for obj in self.profile_params:
            if obj.param_name in added_item_names:
                continue
            pp_unit_info = {}
            if obj.pp_unit_option:
                pp_unit_info = {k: getattr(obj.pp_unit_option.unit_option, k)
                                for k in ['param_default', 'conversion_factor',
                                          'symbol']}  # TODO dont need symbol
                # for k in ['param_default', 'conversion_factor', 'symbol']}

            resp_data['unit_info'].append(pp_unit_info)
            added_item_names.append(obj.param_name)
