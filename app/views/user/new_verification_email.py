from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.tasks.user_admin import send_verification_email


class NewVerificationEmail(APIView):

    def get(self, request):
        if not request.user.username.startswith('demo_'):
            send_verification_email.delay(request.user.id)
        return Response({'status': 'Success'}, status=status.HTTP_200_OK)
