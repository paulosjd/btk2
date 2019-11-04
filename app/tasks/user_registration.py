from celery.utils.log import get_task_logger
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from btk2.activate import account_activation_token
from btk2.celery import celery_app
from btk2.settings import DEFAULT_DOMAIN, EMAIL_HOST_USER, FRONTEND_HOME

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
    tmpl_c = {'username': user.username, 'home_login': FRONTEND_HOME + '/login'}
    email_body = render_to_string('username_reminder.html', tmpl_c)

    try:
        send_mail(
            'Body Metrics Tracker - username reminder',
            email_body, EMAIL_HOST_USER,
            [user.email], fail_silently=True,
        )
    except IOError as e:
        log.debug(e)


@celery_app.task
def send_password_reset_email(email_dct):
    """ Invokes Django builtin password reset functionality
    :param email_dct: dict with an 'email' key for an email address string
    :type email_dct: dict
    :return None
    """
    form = PasswordResetForm({'email': email_dct})
    if form.is_valid():
        request = HttpRequest()
        request.META.update({
            'SERVER_NAME': DEFAULT_DOMAIN,
            'SERVER_PORT': '80'
        })
        form.save(
            request=request,
            use_https=False,
            from_email=EMAIL_HOST_USER,
            subject_template_name='password_reset_subject.txt'
        )


@celery_app.task
def send_verification_email(user_id):
    try:
        user = User.objects.get(pk=user_id)
        tmpl_c = {
            'user': user,
            'domain': f'http://{DEFAULT_DOMAIN}',
            'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
            'token': account_activation_token.make_token(user),
        }
        email_body = render_to_string('account_activation_email.html', tmpl_c)
        try:
            send_mail(
                'Verify your Health Metric Tracker profile',
                email_body, EMAIL_HOST_USER, [user.email],
                fail_silently=False,
            )
        except IOError as e:
            log.debug(e)

    except ObjectDoesNotExist:
        log.warning(f'send_verification_email failed. user_id: {user_id}')
