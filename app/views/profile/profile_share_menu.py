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
             'active_shares': profile.get_active_shares(),
             'share_requests_received': profile.get_share_requests(),
             'share_requests_made': profile.get_share_requests('made'),
             **serializer.data}, status=status.HTTP_200_OK)

    def get(self, request):
        profile = request.user.profile
        if not self.search_text:
            return self.profile_data_response(profile)

        profile_qs = Profile.objects.verified().filter(
                user__username__icontains=self.search_text,
            ).exclude(
                id=profile.id
            ).exclude(
                id__in=profile.shares_requested.values_list('receiver_id')
            ).exclude(
                id__in=[a['profile_id'] for a in profile.get_active_shares()]
            ).annotate(name=F('user__username')).values('id', 'name')

        return Response(profile_qs, status=status.HTTP_200_OK)

    def post(self, request):
        profile = request.user.profile
        if self.action not in ['request', 'accept', 'delete']:
            return Response({'error': 'Param not in [request, accept, delete]'},
                            status=status.HTTP_400_BAD_REQUEST)

        if self.action == 'request':
            receiver = get_object_or_404(
                Profile.objects,
                id=request.data.get('profile_id')
            )
            ProfileShare.objects.create(
                requester=profile, receiver=receiver,
                message=request.data.get('message', '')
            )
            return self.profile_data_response(profile)

        instance = get_object_or_404(
            ProfileShare,
            id=request.data.get('profile_share_id')
        )

        if self.action == 'delete':
            instance.delete()
        else:
            instance.enabled = True
            instance.save()

        return self.profile_data_response(profile)
