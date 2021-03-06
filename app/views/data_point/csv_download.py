import csv
import logging
from typing import List

from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import DataPoint, Parameter, ProfileParamUnitOption
from app.serializers import DataPointSerializer

log = logging.getLogger(__name__)


class CsvDownloadView(APIView):
    serializer_class = DataPointSerializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parameters = []
        self.param_cols = {}

    def post(self, request):
        """
        :param request: dict, if key 'meta' provided this is must be a dict
        :return: DRF Response object
        """
        date_fmt, param_names = [request.data.get(s) for s in
                                 ['date_fmt', 'fields']]
        date_fmt = Parameter.date_fmt_opts_map.get(date_fmt)
        profile = request.user.profile

        if date_fmt and param_names:
            parameters = [Parameter.objects.unfiltered().get(name=field)
                          for field in param_names]
            self.init(parameters, date_fmt)

            header_labels = self.get_headers_labels()
            rows = self.get_rows()

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = \
                f'attachment; filename="{profile.user.username}_data.csv"'
            writer = csv.writer(response)
            writer.writerow(header_labels)
            for row in rows:
                writer.writerow(row)

            return response

        log.error(f'CsvDownload bad request. date_fmt: {date_fmt} '
                  f'param_names: {param_names} profile: {profile}')
        return Response({'error': 'Bad request'},
                        status=status.HTTP_400_BAD_REQUEST)

    def init(self, parameters, dt_fmt) -> None:
        for param in parameters:
            param_dpts = DataPoint.objects.filter(
                profile=self.request.user.profile, parameter=param
            ).all()
            param_sub_rows = [
                [getattr(a, field) for field in param.upload_fields.split(', ')]
                for a in param_dpts
            ]
            for ind, ps in enumerate(param_sub_rows):
                param_sub_rows[ind][0] = param_sub_rows[ind][0].strftime(dt_fmt)
            self.param_cols[param.name] = param_sub_rows
            self.parameters.append(param)
        self.parameters = list(reversed(sorted(
            self.parameters, key=lambda x: len(self.param_cols[x.name])
        )))

    def get_headers_labels(self) -> List[str]:
        """ Returns data for use by csv writer """
        header_labels = []
        first = True

        for parameter in self.parameters:
            unit_option = ProfileParamUnitOption.get_unit_option(
                self.request.user.profile, parameter
            )
            param_labels = [
                f"{a.title().rstrip('s')} ({unit_option.symbol})"
                if ind != 0 else a.title().rstrip('s')
                for ind, a in enumerate(
                    parameter.upload_field_labels.split(', '))
            ]
            if not first:
                param_labels.insert(0, '')
            first = False
            header_labels.extend(param_labels)

        return header_labels

    def get_rows(self) -> List[List[str]]:
        """ Returns list of lists containing strings used by csv writer """
        rows = []
        max_col_len = max([len(i) for i in self.param_cols.values()])
        for row_num in range(max_col_len):
            row = []
            first = True
            for parameter in self.parameters:
                try:
                    sub_row = self.param_cols[parameter.name][row_num]
                except IndexError:
                    sub_row = ['' for _ in range(parameter.num_values + 1)]
                if not first:
                    sub_row.insert(0, '')
                row.extend(sub_row)
                first = False
            rows.append(row)

        return rows
