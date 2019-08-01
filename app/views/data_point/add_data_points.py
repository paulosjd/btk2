from datetime import datetime

from app.models import DataPoint, Parameter
from .dp_base import BaseDataPointsView


class AddDataPoints(BaseDataPointsView):

    def post(self, request):
        form_data = request.data.get('value')
        parameter = Parameter.objects.filter(
            name=form_data.get('parameter')).first()
        if form_data and parameter:
            self.process_post_data(form_data, parameter)
        return self.json_response()

    def process_post_data(self, form_data, parameter):
        param_fields = parameter.upload_fields.split(', ')
        row_nums = set([k.split('_')[0] for k in form_data.keys()
                        if k and k.split('_')[0].isdigit()])
        for num in row_nums:
            try:
                dp_data = {field: form_data[f'{num}_{field}']
                           for field in param_fields + ['date']}
            except KeyError:
                continue
            if not all(dp_data.values()):
                continue
            for k, v in dp_data.items():
                try:
                    dp_data[k] = datetime.strptime(dp_data[k], '%Y-%m-%d') \
                        if k == 'date' else round(float(dp_data[k]), 1)
                except ValueError:
                    continue

            DataPoint.update_on_date_match_or_create(
                parameter=parameter, profile=self.request.user.profile,
                **dp_data
            )
