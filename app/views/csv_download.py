import csv
import json
import logging

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import DataPoint, Parameter
from app.serializers import DataPointSerializer
from app.utils import CsvToModelData

log = logging.getLogger(__name__)


class CsvDownloadView(APIView):
    serializer_class = DataPointSerializer

    def post(self, request):
        """
        :param request: dict, if key 'meta' provided this is must be a dict
        :return: DRF Response object
        """
        date_fmt, fields = [request.data.get(s) for s in ['date_fmt', 'fields']]
        date_fmt = Parameter.date_fmt_opts_map.get(date_fmt)
        profile = request.user.profile
        if date_fmt and fields:
            datapoints = DataPoint.objects.filter(profile=profile, parameter__name__in=fields).all()
            field_dps = [[rec for rec in datapoints if rec.parameter.name == field] for field in fields]
            print(field_dps)
            print(fields)
            print(datapoints)

            # Create the HttpResponse object with the appropriate CSV header.
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="profile_data.csv"'
            writer = csv.writer(response)
            writer.writerow(['First row', 'Foo', 'Bar', 'Baz'])
            writer.writerow(['Second row', 'A', 'B', 'C', '"Testing"', "Here's a quote"])

            return response

        log.error(f'CsvDownload bad request. date_fmt: {date_fmt} fields: {fields} profile: {profile}')
        return Response({'error': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)
