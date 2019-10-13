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
from app.utils import CalcParamIdeal, get_monthly_changes, get_rolling_mean

log = logging.getLogger(__name__)


class ProfileSummaryData(APIView):
    param_fields = ['name', 'upload_fields', 'upload_field_labels',
                    'num_values', 'ideal_info', 'ideal_info_url',
                    'available_unit_options', 'id']
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
                      **ProfileParamUnitOption.param_unit_opt_dct(
                          obj.unit_option)}
                     for obj in null_data_params],
            })
            self.update_with_ideals_data(resp_data, profile)
            self.update_with_units_options(resp_data)
            self.update_with_stats_data(resp_data)
            return Response(resp_data, status=status.HTTP_200_OK)
        return Response({'status': 'Bad request',
                         'errors': serializers['profile_summary'].errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def get_serializers(self, profile):
        bookmarks = profile.get_bookmarks_data()
        summary_data = profile.get_summary_data()
        all_data = [{**{field: getattr(obj, field) for field in
                        ['id', 'date', 'value', 'value2', 'qualifier']},
                     **{'parameter': obj.parameter.name,
                        'num_values': obj.parameter.num_values}}
                    for obj in profile.all_datapoints()]
        avail_params = [
            {field: getattr(obj, field) for field in self.param_fields}
            for obj in Parameter.objects.all()
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

    def update_with_units_options(self, resp_data):
        """ Updates resp_data with the key unit_info """
        resp_data['unit_info'] = []
        added_item_names = []
        for obj in self.profile_params:
            pp_unit_info = {}
            if obj.param_name not in added_item_names:
                pp_unit_info = ProfileParamUnitOption.get_unit_info(obj)
            if pp_unit_info:
                resp_data['unit_info'].append(pp_unit_info)
                added_item_names.append(obj.param_name)

    @staticmethod
    def update_with_stats_data(resp_data):
        """ Updates the dict passed in with data returned from helper functions
        :param resp_data: dict containing data with expected structure
        :return: None
        """
        resp_data.update({k: [] for k in ['rolling_means', 'monthly_changes']})
        data_points = resp_data['datapoints']
        param_names = set([a['parameter'] for a in data_points])
        for pn in param_names:
            param_dps = [a for a in data_points if a['parameter'] == pn]
            resp_data['rolling_means'].append(
                get_rolling_mean(param_dps, extra={'param_name': pn}))
            resp_data['monthly_changes'].append(
                get_monthly_changes(param_dps, extra={'param_name': pn})
            )
