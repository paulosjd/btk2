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

    def dispatch(self, request, *args, **kwargs):
        self.search_text = kwargs.pop('search', '').strip()
        self.action = kwargs.pop('action', '')
        return super().dispatch(request, *args, **kwargs)

    def profile_data_response(self, profile):
        serializer = self.serializer_class(profile)
        return Response(
            {'is_verified': profile.email_confirmed,
             'share_requests_received': profile.get_share_requests(),
             'share_requests_made': profile.get_share_requests('made'),
             **serializer.data}, status=status.HTTP_200_OK)

    def get(self, request):
        profile = request.user.profile
        if not self.search_text:
            return self.profile_data_response(profile)

        qs = Profile.objects.verified().filter(
            user__username__icontains=self.search_text,
        ).exclude(id=profile.id).exclude(
            id__in=profile.shares_requested.values_list('receiver_id')
        ).annotate(name=F('user__username')).values('id', 'name')
        return Response(qs, status=status.HTTP_200_OK)

    def post(self, request):
        print(request.data)
        profile = request.user.profile
        if self.action not in ['request', 'accept']:
            return Response({'error': 'Param not in [request, accept]'},
                            status=status.HTTP_400_BAD_REQUEST)

        if self.action == 'request' and request.data.get('profile_id'):
            rec = get_object_or_404(Profile.objects,
                                    id=request.data['profile_id'])
            ProfileShare.objects.create(requester=profile, receiver=rec,
                                        message=request.data.get('message', ''))
            return self.profile_data_response(profile)

        if 3 == request:
            return Response({}, status=status.HTTP_200_OK)
        return Response({'status': 'Bad request'},
                        status=status.HTTP_400_BAD_REQUEST)
