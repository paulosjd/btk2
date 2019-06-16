from django.contrib.auth import views as auth
from django.urls import path

from .views.csv_upload import CsvUpload
from .views.profile_summary import ProfileSummary
from .views.user.login_help import LoginHelp
from .views.user.password_reset import PasswordReset
from .views.user.registration import RegistrationAPIView

urlpatterns = [
    path('test', CsvUpload.as_view(), name='csv-upload'),
    path('users/registration', RegistrationAPIView.as_view()),
    path('users/help/<forgot>', LoginHelp.as_view()),
    path('users/password-reset', PasswordReset.as_view()),

    path('reset/<uidb64>/<token>/', auth.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('profile/<int:user_id>/summary', ProfileSummary.as_view())
    # do need to send across user_id - can get from jwt?  -
    # or other thing in header ?
]
