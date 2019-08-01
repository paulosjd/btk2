from app.models import DataPoint
from .dp_base import BaseDataPointsView


class EditDataPoints(BaseDataPointsView):

    def post(self, request):
        form_data = request.data.get('value')
        if form_data and form_data.get('parameter'):
            dp_ids = set([a.split('_')[0] for a in form_data.keys()
                          if a and a.split('_')[0].isdigit()])
            for dp_id in dp_ids:
                try:
                    dp_record = DataPoint.objects.get(id=dp_id)
                except DataPoint.DoesNotExist:
                    continue
                if dp_record.id in form_data.get('delItems'):
                    dp_record.delete()
                else:
                    for field in ['date', 'value', 'value2']:
                        val = form_data.get(f'{dp_record.id}_{field}')
                        if val:
                            setattr(dp_record, field, val)
                    dp_record.save()

        return self.json_response()
