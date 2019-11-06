import logging

from django.db.models import F
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import Profile, ProfileShare
from app.serializers import ProfileSerializer

log = logging.getLogger(__name__)


class ProfileShareMenu(APIView):
    serializer_class = ProfileSerializer
    search_text = ''
    action = ''
    profile = None

    def dispatch(self, request, *args, **kwargs):
        self.search_text = kwargs.pop('search', '').strip()
        self.action = kwargs.pop('action', '')
        self.profile = request.user.profile
        return super().dispatch(request, *args, **kwargs)

    def profile_data_response(self):
        serializer = self.serializer_class(self.profile)
        return Response(
            {'is_verified': self.profile.email_confirmed,
             **serializer.data}, status=status.HTTP_200_OK)

    def get(self, request):
        if not self.search_text:
            return self.profile_data_response()

        qs = Profile.objects.verified().filter(
            user__username__icontains=self.search_text,
        ).exclude(id=self.profile.id).exclude(
            id__in=self.profile.shares_requested.values_list('receiver_id')
        ).annotate(name=F('user__username')).values('id', 'name')
        return Response(qs, status=status.HTTP_200_OK)

    def post(self, request):
        print(request.data)
        if self.action not in ['request', 'accept']:
            return Response({'error': 'Param not in [request, accept]'},
                            status=status.HTTP_400_BAD_REQUEST)

        if self.action == 'request' and request.data.get('profile_id'):
            rec = get_object_or_404(Profile.objects,
                                    id=request.data['profile_id'])
            ProfileShare.objects.create(
                requester=request.user.profile, receiver=rec,
                message=request.data.get('message_id')
            )
            return self.profile_data_response()

        if 3 == request:
            return Response({}, status=status.HTTP_200_OK)
        return Response({'status': 'Bad request'},
                        status=status.HTTP_400_BAD_REQUEST)
