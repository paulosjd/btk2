import tempfile
from datetime import datetime

from celery.result import AsyncResult
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.tasks.generate_report import profile_report_pdf


class ProfileReportView(APIView):
    task_id = ''

    def dispatch(self, request, *args, **kwargs):
        self.task_id = kwargs.pop('task_id', '')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        print(self.task_id)
        print(request)

    def post(self, request):
        print(request.data)
        date = request.data.get('date', '')
        param_ids = request.data.get('param_ids', [])
        removed_stats = request.data.get('removed_stats', [])
        print(date)
        print(param_ids)
        print(removed_stats)
        if date and param_ids:
            fn = f'{request.user.username}_report_{datetime.now():%Y%b%d}.pdf'
            task = profile_report_pdf.delay(
                request.user.profile.id, fn, date_str=date, param_ids=param_ids,
                removed_stats=removed_stats
            )
            return Response(
                # {'file_name': fn},
                {'task_id': task.id},
                status=status.HTTP_202_ACCEPTED,
                headers={'Location': 'Test location'}
            )
            # response['Location'] = 'Test location'
        return Response({'status': 'Bad request'},
                        status=status.HTTP_400_BAD_REQUEST)
