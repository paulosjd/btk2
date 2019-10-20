from abc import ABCMeta, abstractmethod

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.serializers import DataPointSerializer
from app.views.profile import ProfileSummaryData


class BaseDataPointsView(APIView):
    __metaclass__ = ABCMeta
    serializer_class = DataPointSerializer

    @abstractmethod
    def post(self, request):
        raise NotImplementedError

    def json_response(self):

        fields = ['id', 'date', 'value', 'value2', 'qualifier']
        all_dps = self.request.user.profile.all_datapoints()

        all_data = [{
            'parameter': obj.parameter.name,
            'num_values': obj.parameter.num_values,
            **{k: getattr(obj, k) for k in fields},
            **{k: getattr(obj.parameter, k) for k in [f'value2_short_label_{n}'
                                                      for n in [1, 2]]}
        } for obj in all_dps]

        serializer = self.serializer_class(data=all_data, many=True)
        if serializer.is_valid():
            dps_dct = {
                'datapoints': [
                    {'parameter': obj.parameter.name,
                     **{k: getattr(obj, k) for k in fields}}
                    for obj in all_dps],
                'all_data': serializer.data
            }
            ProfileSummaryData.update_with_stats_data(dps_dct)
            del dps_dct['datapoints']

            return Response(dps_dct, status=status.HTTP_200_OK)

        return Response({'status': 'Bad request',
                         'errors': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)
