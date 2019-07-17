from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import DataPoint, Parameter
from app.serializers import DataPointSerializer
from app.utils import CsvToModelData


class CsvUploadView(APIView):
    serializer_class = DataPointSerializer

    def post(self, request):
        """
        :param request: dict, if key 'meta' provided this is must be a dict
        :return: DRF Response object
        """
        # First check for confirm data of uploaded file
        confirm_data = request.data.get('data')
        if confirm_data and all([confirm_data.get(s) for s in ['confirm', 'data', 'meta']]):
            param_id = confirm_data.get('meta').get('param_id')
            data_list = [{**con_dct, **{'parameter': param_id, 'profile': request.user.profile.id}}
                         for con_dct in confirm_data['data']]
            serializer = self.serializer_class(data=data_list, many=True)
            error_msg = 'Something has gone wrong'
            if serializer.is_valid():
                parameter = get_object_or_404(Parameter.objects, id=param_id)
                for val_data in serializer.data:
                    val_data.update({'parameter': parameter, 'profile': request.user.profile})
                bulk_create_result = DataPoint.bulk_create_from_csv_upload(serializer.data)
                if bulk_create_result.message:
                    error_msg = bulk_create_result.message
                if bulk_create_result.success:
                    return Response({'status': 'Success'}, status=status.HTTP_200_OK)
            return Response({'error': error_msg}, status=status.HTTP_400_BAD_REQUEST)

        # Check for uploaded file etc
        print(request.data.get('unit_choice'))
        print(request.data.get('unit_option'))
        print(request.data.get('unit_option'))

        upload_data = request.data.get('file')
        date_fmt = Parameter.date_fmt_opts_map.get(request.data.get('date_format'))
        if upload_data and date_fmt:
            parameter = Parameter.objects.filter(name=request.data.get('param_choice')).first()
            if parameter and parameter.upload_fields:
                meta_dict = {
                    'field_order': parameter.upload_fields.split(', '),
                    'param_id': parameter.id,
                    'date_fmt': date_fmt
                }
                csv_to_data = CsvToModelData(upload_data, meta_dict)
                if csv_to_data.is_valid:
                    return Response({'data': [{k: getattr(obj, k) for k in meta_dict['field_order']}
                                              for obj in csv_to_data],
                                     'meta': meta_dict},
                                    status=status.HTTP_200_OK)
                return Response({'error': csv_to_data.error},
                                status=status.HTTP_400_BAD_REQUEST)

        return Response({'error': 'Bad request'},
                        status=status.HTTP_400_BAD_REQUEST)
