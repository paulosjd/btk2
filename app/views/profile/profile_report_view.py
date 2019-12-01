import logging
import os
from datetime import datetime

from celery.result import AsyncResult
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.tasks.generate_report import profile_report_pdf

log = logging.getLogger(__name__)


class ProfileReportView(APIView):
    task_id = ''

    def dispatch(self, request, *args, **kwargs):
        self.task_id = kwargs.pop('task_id', '')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        if not self.task_id:
            return Response({'status': 'Bad request'},
                            status=status.HTTP_400_BAD_REQUEST)
        task_result = AsyncResult(self.task_id)
        if task_result.ready():
            fnme = f'{request.user.username}_report_{datetime.now():%Y%b%d}.pdf'
            try:
                with open(task_result.result, 'r') as pdf:
                    response = HttpResponse(
                        pdf.read(), content_type='application/pdf'
                    )
                    response['Content-Disposition'] = f'inline;filename={fnme}'
            except FileNotFoundError:
                return Response(status=status.HTTP_204_NO_CONTENT)
            try:
                os.remove(task_result.result)
            except OSError as e:
                log.error(e)
            return response

        return Response({'status': 'Not ready'}, status=status.HTTP_200_OK)

    def post(self, request):
        date = request.data.get('date', '')
        param_ids = request.data.get('param_ids', [])
        removed_stats = request.data.get('removed_stats', [])
        if date and param_ids:
            task = profile_report_pdf.delay(
                request.user.profile.id, date_str=date, param_ids=param_ids,
                removed_stats=removed_stats
            )
            return Response(
                {'task_id': task.id},
                status=status.HTTP_202_ACCEPTED,
                # headers={'Location': 'Test location'}
            )
        return Response({'status': 'Bad request'},
                        status=status.HTTP_400_BAD_REQUEST)
