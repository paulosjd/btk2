import logging
from collections import namedtuple

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import Parameter, ProfileParamUnitOption
from app.serializers import (
    BookmarkSerializer, DataPointSerializer, ParameterSerializer,
    SummaryDataSerializer
)
from app.utils.calc_param_ideal import CalcParamIdeal
from app.utils.view_helpers import (
    get_summary_data, param_unit_opt_dct, get_rolling_mean
)

log = logging.getLogger(__name__)


class ProfileSummaryData(APIView):
    param_fields = ['name', 'upload_fields', 'upload_field_labels',
                    'num_values', 'ideal_info', 'ideal_info_url',
                    'available_unit_options']
    profile_params = []
    all_measurements = []

    def get(self, request):
        profile = request.user.profile
        serializers = dict(zip(
            ['profile_summary', 'all_params', 'datapoints', 'bookmarks'],
            self.get_serializers(profile)
        ))
        if all([ser.is_valid() for ser in serializers.values()]):
            resp_data = {k: v.data for k, v in serializers.items()}
            null_data_params = ProfileParamUnitOption.null_data_params(profile)
            resp_data.update({
                'date_formats': Parameter.date_formats,
                'blank_params':
                    [{**{field: getattr(obj.parameter, field)
                         for field in self.param_fields},
                      **param_unit_opt_dct(obj.unit_option)}
                     for obj in null_data_params],
            })
            self.update_with_ideals_data(resp_data, profile)
            self.update_with_units_options(resp_data)
            self.update_with_rolling_means(resp_data)

            return Response(resp_data, status=status.HTTP_200_OK)
        return Response({'status': 'Bad request',
                         'errors': serializers['profile_summary'].errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def get_serializers(self, profile):
        summary_data = get_summary_data(profile)
        all_data = [{**{field: getattr(obj, field) for field in
                        ['id', 'date', 'value', 'value2', 'qualifier']},
                     **{'parameter': obj.parameter.name,
                        'num_values': obj.parameter.num_values}}
                    for obj in profile.all_datapoints()]
        avail_params = [
            {field: getattr(obj, field) for field in self.param_fields}
            for obj in Parameter.objects.all()
        ]
        bookmarks = [
            {field: getattr(obj, field) for field in
             ['id', 'url', 'title', 'param_name']}
            for obj in profile.user_bookmarks.all()
        ]
        return [serializer(data=data, many=True) for (serializer, data) in [
            (SummaryDataSerializer, summary_data),
            (ParameterSerializer, avail_params),
            (DataPointSerializer, all_data),
            (BookmarkSerializer, bookmarks)
        ]]

    def update_with_ideals_data(self, resp_data, profile):
        resp_data['ideals'] = []
        ProfileParamObj = namedtuple('profile_param_obj',
                                     ['param_name', 'pp_unit_option'])
        Item = namedtuple('UnitOptLookupData',
                          ['param_name', 'value', 'value2'])
        profile_summary_items = [
            Item(obj['parameter']['name'],
                 obj['data_point']['value'],
                 obj['data_point']['value2'])
            for obj in resp_data['profile_summary']
        ]
        blank_param_items = [Item(obj['name'], None, None)
                             for obj in resp_data['blank_params']]
        profile_params = profile_summary_items + blank_param_items

        for obj in profile_params:
            try:
                profile_param = ProfileParamUnitOption.objects.get(
                    parameter__name=obj.param_name, profile=profile
                )
            except ProfileParamUnitOption.DoesNotExist:
                profile_param = None
                param_ideal = CalcParamIdeal(obj.param_name, profile)
                ideal_data = param_ideal.get_ideal_data()
                target_data = {'saved': None,
                               'saved2': None,
                               'missing_field': param_ideal.required_field,
                               'misc_info': param_ideal.misc_data,
                               'param_name': obj.param_name}
                target_data.update({
                    k: ideal_data.get(k, '') for k in
                    ['ideal', 'ideal2', 'ideal_prepend', 'ideal2_prepend']
                })
            else:
                target_obj = profile_param.targets(obj.value, obj.value2)
                target_data = {'missing_field': target_obj.required_field,
                               'misc_info': target_obj.misc_data,
                               'param_name': obj.param_name}
                target_data.update({
                    k: getattr(target_obj, k) for k in
                    ['saved', 'saved2', 'ideal', 'ideal2', 'ideal_prepend',
                     'ideal2_prepend']
                })
            resp_data['ideals'].append(target_data)
            self.profile_params.append(
                ProfileParamObj(obj.param_name, profile_param)
            )

    @staticmethod
    def update_with_rolling_means(resp_data):
        """ Updates resp_data with the key rolling_means """
        resp_data['rolling_means'] = []
        data_points = resp_data['datapoints']
        param_names = set([a['parameter'] for a in data_points])
        for pn in param_names:
            param_dps = [a for a in data_points if a['parameter'] == pn]
            resp_data['rolling_means'].append(
                get_rolling_mean(
                    param_dps[-1]['date'],
                    param_dps[0]['date'],
                    data_points=param_dps,
                    meta={'param_name': pn}
                ))

    def update_with_units_options(self, resp_data):
        """ Updates resp_data with the key unit_info """
        resp_data['unit_info'] = []
        added_item_names = []
        for obj in self.profile_params:
            pp_unit_info = {}
            if obj.param_name not in added_item_names:
                pp_unit_info = self.get_profile_param_unit_info(obj)
            if pp_unit_info:
                resp_data['unit_info'].append(pp_unit_info)
                added_item_names.append(obj.param_name)

    @staticmethod
    def get_profile_param_unit_info(obj):
        """
        :param obj: expected to have 'param_name' and 'pp_unit_info' attributes
        :return: dict or None
        """
        if obj.pp_unit_option:
            pp_unit_info = {
                k: getattr(obj.pp_unit_option.unit_option, k)
                for k in ['param_default', 'conversion_factor', 'symbol']
            }
            pp_unit_info['param_name'] = obj.param_name
            pp_unit_info.update({
                k: getattr(obj.pp_unit_option, k) for k in
                ['color_hex', 'color_range_val_1', 'color_range_val_2']
            })
            return pp_unit_info
