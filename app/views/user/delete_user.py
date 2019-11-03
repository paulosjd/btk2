from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class DeleteUserView(APIView):

    def post(self, request):
        confirm_del = request.data.get('confirm_delete')
        if confirm_del is True:
            request.user.delete()
            return Response({'user_del': 'Success'}, status=status.HTTP_200_OK)
        return Response({'status': 'Bad request'},
                        status=status.HTTP_400_BAD_REQUEST)
