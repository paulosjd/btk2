# main/tasks.py

import logging

from django.core.mail import send_mail
from django.contrib.auth.models import User

from btk2.celery import celery_app

log = logging.getLogger(__name__)


@celery_app.task
def send_verification_email(user_id):
    try:
        user = User.objects.get(pk=user_id)
        send_mail(
            'Follow this link to verify your account: '
            # 'http://localhost:8000' % reverse('verify', kwargs={
            #     'uuid': str(user.verification_uuid)}),
            'funcmols@gmail.com',
            ['pj_davis@hotmail.co.uk'],
            # [user.email],
            fail_silently=False,
        )
        log.warning(f'send_verification_email done. user_id: {user_id}')
    except User.DoesNotExist:
        log.warning(f'send_verification_email failed. user_id: {user_id}')