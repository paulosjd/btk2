from abc import ABCMeta, abstractmethod

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.serializers import BookmarkSerializer


class BaseBookmarksView(APIView):
    __metaclass__ = ABCMeta
    serializer_class = BookmarkSerializer
    profile = None

    @abstractmethod
    def post(self, request):
        raise NotImplementedError

    def json_response(self):
        bookmarks_data = self.profile.get_bookmarks_data()
        serializer = self.serializer_class(data=bookmarks_data, many=True)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({'status': 'Bad request', 'errors': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)
