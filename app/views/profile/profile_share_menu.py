from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.serializers import ProfileSerializer


class ProfileShareMenu(APIView):
    serializer_class = ProfileSerializer

    def get(self, request):
        serializer = self.serializer_class(request.user.profile)
        return Response({'is_verified': request.user.profile.email_confirmed,
                         **serializer.data},
                        status=status.HTTP_200_OK)

    def post(self, request):
        print(request.data)
        if 3 == request:
            return Response({}, status=status.HTTP_200_OK)
        return Response({'status': 'Bad request'},
                        status=status.HTTP_400_BAD_REQUEST)
