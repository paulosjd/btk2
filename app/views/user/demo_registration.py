from calendar import timegm
from datetime import datetime
import uuid

from django.contrib.auth import get_user_model
import jwt
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings

from btk2.settings import SECRET_KEY
from app.serializers import RegistrationSerializer

User = get_user_model()
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER


class DemoRegistrationAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer

    def get(self, request):

        my_user = User.objects.create(is_temporary=True,
                                      username=f'demo_{uuid.uuid4().hex[:16]}')
        payload = jwt_payload_handler(my_user)
        if api_settings.JWT_ALLOW_REFRESH:
            payload['orig_iat'] = timegm(datetime.utcnow().utctimetuple())
        # serializer.data.update({'token': jwt.encode(payload, SECRET_KEY)})
        return Response(
            dict(token=jwt.encode(payload, SECRET_KEY), ), #**serializer.data
            status=status.HTTP_201_CREATED
        )

        #
        # return Response({'status': 'Bad request', 'errors': errors},
        #                 status=status.HTTP_400_BAD_REQUEST)
