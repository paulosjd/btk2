from django.contrib.auth import login, get_user_model
from django.contrib.auth.views import PasswordResetCompleteView
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.shortcuts import redirect, render
from django.utils import six
from django.utils.http import urlsafe_base64_decode

from .settings import FRONTEND_HOME

User = get_user_model()


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.profile.email_confirmed)
        )


account_activation_token = AccountActivationTokenGenerator()


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        login(request, user)
        return redirect(FRONTEND_HOME)

    return render(request, 'account_activation_invalid.html')


class PasswordResetIsCompleteView(PasswordResetCompleteView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['home_login'] = FRONTEND_HOME + '/login'
        return context
