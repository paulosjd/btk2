from celery.utils.log import get_task_logger
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest

from btk2.celery import celery_app

log = get_task_logger(__name__)

User = get_user_model()


@celery_app.task
def send_username_reminder_email(email):
    """ Sends an email containing the username which corresponds to the account
    with the provided email address, if it exists
    :param email: email address
    :type email: str
    :return None
    """
    try:
        user = User.objects.get(email=email)
    except ObjectDoesNotExist:
        return
    try:
        send_mail(
            'Body Metrics Tracker -- username reminder',
            f'Username for the account registered to this email address '
            f'is: {user.username}', 'funcmols@gmail.com',
            [user.email], fail_silently=True,
        )
    except IOError as e:
        log.debug(e)


@celery_app.task
def send_password_reset_email(email_dct):
    """ Invokes Django ...
    :param email_dct: dict with an 'email' key for an email address string
    :type email_dct: dict
    :return None
    """
    form = PasswordResetForm({'email': email_dct})
    if form.is_valid():
        request = HttpRequest()
        request.META['SERVER_NAME'] = 'localhost'
        request.META['SERVER_PORT'] = '80'
        form.save(
            request=request,
            use_https=False,
            from_email='funcmols@gmail.com',
        )


@celery_app.task
def send_verification_email(user_id, user=None):
    try:
        user = user or User.objects.get(pk=user_id)
        try:
            send_mail(
                'test_subject',
                'Follow this link to verify your account: ',
                'funcmols@gmail.com',
                [user.email],
                fail_silently=False,
            )
        except IOError as e:
            log.debug(e)

    except ObjectDoesNotExist:
        log.warning(f'send_verification_email failed. user_id: {user_id}')
