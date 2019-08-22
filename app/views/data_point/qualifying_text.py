from app.models import DataPoint
from .dp_base import BaseDataPointsView


class QualifyingTextCrudView(BaseDataPointsView):

    def post(self, request):
        req_data = request.data.get('value', {})
        datapoint = DataPoint.objects.filter(id=req_data.get('objId')).first()
        qualify_text = req_data.get('qualify_text')
        if datapoint and qualify_text is not None:
            max_len = DataPoint._meta.get_field('qualifier').max_length
            datapoint.qualifier = qualify_text[:max_len]
            datapoint.save()
        return self.json_response()
