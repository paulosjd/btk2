from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.tasks.user_registration import send_verification_email


class NewVerificationEmail(APIView):

    def get(self, request):
        send_verification_email.delay(None, request.user)
        return Response({'status': 'Success'}, status=status.HTTP_200_OK)
