from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import Parameter, ProfileParamUnitOption, UnitOption
from app.utils.calc_param_ideal import CalcParamIdeal


class TargetUpdateView(APIView):

    def get(self, request):
        return self.json_response(request.user.profile)

    def post(self, request):
        profile = request.user.profile
        post_data = request.data.get('value', {})
        param_name, target_value, target_value2 = [post_data.get(s) for s in [
            'param_name', 'target_value', 'target_value2']]
        if not param_name or target_value is None and target_value2 is None:
            return self.json_response(profile)

        if target_value == '':
            target_value = None
        elif not target_value2 and target_value is not None:
            try:
                target_value = round(float(target_value), 1)
            except ValueError:
                return self.json_response(profile)

        if target_value2 == '':
            target_value2 = None
        elif not target_value and target_value2 is not None:
            try:
                target_value2 = round(float(target_value2), 1)
            except ValueError:
                return self.json_response(profile)
        parameter = get_object_or_404(Parameter.objects, name=param_name)

        try:
            record = ProfileParamUnitOption.objects.get(
                profile=profile, parameter=parameter
            )
        except ProfileParamUnitOption.DoesNotExist:
            ProfileParamUnitOption.objects.create(
                profile=profile, parameter=parameter, target_value=target_value,
                target_value2=target_value2,
                unit_option=UnitOption.get_default_for_param(parameter)
            )
        else:
            if post_data.get('target_value') is not None:
                record.target_value = target_value
            else:
                record.target_value2 = target_value2
            record.save()

        return self.json_response(profile)

    @staticmethod
    def json_response(profile):
        resp_data = []
        for obj in profile.summary_data():
            param_name = obj.parameter.name
            try:
                profile_param = ProfileParamUnitOption.objects.get(
                    parameter__name=param_name, profile=profile
                )
            except ProfileParamUnitOption.DoesNotExist:
                param_ideal = CalcParamIdeal(param_name, profile)
                target_data = {'saved': None,
                               'saved2': None,
                               'ideal': param_ideal.get_ideal(),
                               'misc_info': param_ideal.misc_data}
            else:
                target_obj = profile_param.targets(obj.value)
                target_data = {'saved': target_obj.saved,
                               'saved2': target_obj.saved2,
                               'ideal': target_obj.ideal,
                               'misc_info': target_obj.misc_data}
            resp_data.append(target_data)

        return Response(resp_data, status=status.HTTP_200_OK)
