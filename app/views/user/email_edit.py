from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.serializers import ProfileSerializer


class EmailEditView(APIView):
    serializer_class = ProfileSerializer

    def post(self, request):
        user = request.user
        new_email = request.data.get('value', {}).get('email')
        split_email = new_email.split('@')
        if new_email and len(split_email) == 2 and '.' in split_email[1]:
            user.email = new_email
            user.save()
            return Response({'email': user.email}, status=status.HTTP_200_OK)
        return Response({'status': 'Bad request'},
                        status=status.HTTP_400_BAD_REQUEST)
