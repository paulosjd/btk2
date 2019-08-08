from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from app.serializers.user.user_password import UserPasswordSerializer

User = get_user_model()


class PasswordReset(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        user = None
        new_password = request.data.get('new_password')
        uid = request.data.get('uid', '')
        if uid.isalpha():
            user_id = urlsafe_base64_decode(uid)
            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                pass

        if user and new_password:
            serializer = UserPasswordSerializer(
                instance=user, data={'password': new_password})
            if serializer.is_valid() and serializer.save(
                    request.data.get('token')):
                return Response({'status': 'OK'}, status=status.HTTP_200_OK)

        return Response({'status': 'Bad request', 'errors': 'Invalid'},
                        status=status.HTTP_400_BAD_REQUEST)
