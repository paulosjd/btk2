from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.serializers import ProfileSerializer


class ProfileInfoUpdate(APIView):
    serializer_class = ProfileSerializer

    def get(self, request):
        serializer = self.serializer_class(request.user.profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        field_names = [('birth_year', 0), ('gender', ''), ('height', 0)]
        req_data = {a: request.data.get(a, b) for a, b in field_names}
        profile_data = {a: b if not req_data[a] and req_data[a] != b
                        else req_data[a] for a, b in field_names}
        serializer = self.serializer_class(data=profile_data,
                                           instance=request.user.profile)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'status': 'Bad request'},
                        status=status.HTTP_400_BAD_REQUEST)
