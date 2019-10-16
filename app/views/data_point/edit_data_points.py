import logging
from datetime import datetime as dt

from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response

from app.models import DataPoint
from .dp_base import BaseDataPointsView

log = logging.getLogger(__name__)


class EditDataPoints(BaseDataPointsView):

    def post(self, request):
        form_data = request.data.get('value')
        if form_data and form_data.get('parameter'):
            dp_ids = set([a.split('_')[0] for a in form_data.keys()
                          if a and a.split('_')[0].isdigit()])
            unique_dates = set([v for k, v in form_data.items() if
                                k.endswith('_date')])

            if len(dp_ids) != len(unique_dates):
                print('here!!')
                return Response({'error': 'Ensure dates are unique'},
                                status=status.HTTP_400_BAD_REQUEST)
            dp_records = DataPoint.objects.filter(id__in=dp_ids)
            for dp_record in dp_records:
                if dp_record.id in form_data.get('delItems'):
                    dp_record.delete()
                else:
                    param_fields = dp_record.parameter.upload_fields.split(', ')
                    dp_data = {field: form_data.get(f'{dp_record.id}_{field}')
                               for field in param_fields + ['date']}
                    for k, v in dp_data.items():
                        try:
                            dp_data[k] = dt.strptime(dp_data[k], '%Y-%m-%d')\
                                if k == 'date' else round(float(dp_data[k]), 2)
                        except ValueError:
                            continue

                    if not all(dp_data.values()):
                        continue

                    for field, value in dp_data.items():
                        setattr(dp_record, field, value)
                    try:
                        dp_record.save()
                    except IntegrityError as e:
                        log.error(e)
                        continue

        return self.json_response()
