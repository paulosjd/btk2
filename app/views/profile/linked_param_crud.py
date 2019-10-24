from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import Parameter, ProfileParamUnitOption
from app.serializers import ParameterSerializer


class LinkedParamCrud(APIView):
    serializer_class = ParameterSerializer
    action = ''

    def dispatch(self, request, *args, **kwargs):
        self.action = kwargs.pop('action')
        return super(LinkedParamCrud, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        profile = request.user.profile
        if self.action == 'add':
            id_list = request.data.get('value')
            if isinstance(id_list, list) and len(id_list) == 2:
                params = [get_object_or_404(Parameter, id=i) for i in id_list]
                # if not ProfileParameterLink.objects.filter(
                #         profile=profile, parameters__in=params).exists():
                #     pplink = ProfileParameterLink(profile=profile)
                #     pplink.save()
                #     pplink.parameters.add(*params)
                return Response({
                    'linked_parameters': profile.get_linked_profile_parameters()
                }, status=status.HTTP_200_OK)

        return Response({'error': 'bad request'},
                        status=status.HTTP_400_BAD_REQUEST)
