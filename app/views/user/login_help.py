from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from app.tasks import send_password_reset_email, send_username_reminder_email


class LoginHelp(APIView):
    permission_classes = (AllowAny,)
    email = None
    forgot = None

    def dispatch(self, request, *args, **kwargs):
        self.forgot = kwargs.pop('forgot')
        return super(LoginHelp, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        email = request.data.get('email', {})
        try:
            validate_email(email.get('email'))
        except ValidationError:
            return Response({'status': 'Bad request'},
                            status=status.HTTP_400_BAD_REQUEST)
        if self.forgot == 'password':
            send_password_reset_email.delay(email['email'])
        else:
            send_username_reminder_email.delay(email['email'])
        return Response({'status': 'Success'}, status=status.HTTP_200_OK)
