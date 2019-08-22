from abc import ABCMeta, abstractmethod

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.serializers import DataPointSerializer


class BaseDataPointsView(APIView):
    __metaclass__ = ABCMeta
    serializer_class = DataPointSerializer

    @abstractmethod
    def post(self, request):
        raise NotImplementedError

    def json_response(self):
        all_data = [{**{field: getattr(obj, field) for field in
                        ['id', 'date', 'value', 'value2', 'qualifier']},
                     **{'parameter': obj.parameter.name,
                        'num_values': obj.parameter.num_values}}
                    for obj in self.request.user.profile.all_datapoints()]

        serializer = self.serializer_class(data=all_data, many=True)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({'status': 'Bad request', 'errors': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)
