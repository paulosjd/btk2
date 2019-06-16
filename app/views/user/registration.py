from calendar import timegm
from datetime import datetime

import jwt
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings

from btk2.settings import SECRET_KEY
from app.serializers import RegistrationSerializer

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER


class RegistrationAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        field_names = ['username', 'email', 'password']
        user_data = {k: request.data.get(k, '') for k in field_names}
        serializer = self.serializer_class(data=user_data)

        if serializer.is_valid():
            serializer.save()
            my_user = User.objects.get(username=serializer.data['username'])
            payload = jwt_payload_handler(my_user)
            # Include original issued at time, to allow token refresh
            if api_settings.JWT_ALLOW_REFRESH:
                payload['orig_iat'] = timegm(datetime.utcnow().utctimetuple())
            serializer.data.update({'token': jwt.encode(payload, SECRET_KEY)})
            return Response(
                dict(token=jwt.encode(payload, SECRET_KEY), **serializer.data),
                status=status.HTTP_201_CREATED
            )

        errors = {name: serializer.errors[name][0] for name in field_names
                  if serializer.errors.get(name)}
        return Response({'status': 'Bad request', 'errors': errors},
                        status=status.HTTP_400_BAD_REQUEST)
