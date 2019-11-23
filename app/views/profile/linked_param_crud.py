import logging

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import Parameter, ProfileParamUnitOption
from app.serializers import ParameterSerializer

log = logging.getLogger(__name__)


class LinkedParamCrud(APIView):
    serializer_class = ParameterSerializer
    action = ''

    def dispatch(self, request, *args, **kwargs):
        self.action = kwargs.pop('action')
        return super(LinkedParamCrud, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        profile = request.user.profile

        if self.action == 'add':
            try:
                param_id, linked_param_id = [
                    request.data.get('value')[s] for s in
                    ['parameter_id', 'linked_parameter_id']
                ]
            except (AttributeError, KeyError):
                return Response({'error': 'invalid post data'},
                                status=status.HTTP_400_BAD_REQUEST)

            profile_param = get_object_or_404(
                ProfileParamUnitOption, parameter__id=param_id, profile=profile
            )
            linked_param = Parameter.objects.unfiltered().get(
                id=linked_param_id
            )
            profile_param.linked_parameter = linked_param
            profile_param.save()

        elif self.action == 'edit':
            profile_params = [
                (get_object_or_404(ProfileParamUnitOption, parameter__name=name,
                                   profile=profile),
                 linked_param_id)
                for name, linked_param_id in request.data.items()
            ]

            for instance, param_id in profile_params:
                try:
                    linked_param = Parameter.objects.unfiltered().get(
                        id=param_id) if param_id else None
                except Parameter.DoesNotExist:
                    log.error(f'Lookup failed for param id: {param_id}')
                    return Response({'error': 'invalid linked param id'},
                                    status=status.HTTP_400_BAD_REQUEST)
                instance.linked_parameter = linked_param

            for instance, id_ in profile_params:
                instance.save()

        else:
            return Response({'error': 'Action param not match'},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {'linked_parameters': profile.get_linked_profile_parameters()},
            status=status.HTTP_200_OK
        )
