from datetime import datetime

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.tasks.generate_report import profile_report_pdf


class ProfileReportView(APIView):

    def post(self, request):
        date = request.data.get('date', '')
        param_ids = request.data.get('param_ids', [])
        if date and param_ids:
            fn = f'{request.user.username}_report_{datetime.now():%Y%b%d}.pdf'
            profile_report_pdf.delay(
                request.user.profile_id, date, param_ids,)
            # Location header to tell client where to poll and listen for .. ?
            return Response(
                {'file_name': fn},
                status=status.HTTP_202_ACCEPTED,
                headers={'Location': 'Test location'}
            )
            # response['Location'] = 'Test location'
            return response
        return Response({'status': 'Bad request'},
                        status=status.HTTP_400_BAD_REQUEST)
