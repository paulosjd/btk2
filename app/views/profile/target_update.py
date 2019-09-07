from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import Parameter, ProfileParamUnitOption
from app.utils.calc_param_ideal import CalcParamIdeal


class TargetUpdateView(APIView):

    def post(self, request):
        profile = request.user.profile
        post_data = request.data.get('value', {})
        param_name, target_value = [post_data.get(s) for s in
                                    ['param_name', 'target_value']]
        if not param_name or target_value is None:
            return self.json_response(profile)

        if target_value == '':
            target_value = None
        else:
            try:
                target_value = round(float(target_value), 1)
            except ValueError:
                return self.json_response(profile)
        parameter = get_object_or_404(Parameter.objects, name=param_name)

        try:
            record = ProfileParamUnitOption.objects.get(
                profile=profile, parameter=parameter
            )
            record.target_value = target_value
        except ProfileParamUnitOption.DoesNotExist:
            record = ProfileParamUnitOption.objects.get(
                profile=profile, parameter=parameter, target_value=target_value
            )

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
                               'ideal': param_ideal.get_ideal(),
                               'misc_info': param_ideal.misc_data}
            else:
                target_obj = profile_param.targets(obj.value)
                target_data = {'saved': target_obj.saved,
                               'ideal': target_obj.ideal,
                               'misc_info': target_obj.misc_data}
            resp_data.append(target_data)

        return Response(resp_data, status=status.HTTP_200_OK)
