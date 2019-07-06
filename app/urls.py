from django.urls import path

from .views.profile import (
    ProfileInfoUpdate, ProfileSummaryData,
)
from .views.csv_upload import CsvUploadView
from .views.user import (
    LoginHelp, PasswordReset, RegistrationAPIView
)

urlpatterns = [
    path('users/registration', RegistrationAPIView.as_view()),
    path('users/help/<forgot>', LoginHelp.as_view()),
    path('users/password-reset', PasswordReset.as_view()),

    path('profile/summary', ProfileSummaryData.as_view()),
    path('profile/info-update', ProfileInfoUpdate.as_view()),
    path('upload/datapoints', CsvUploadView.as_view()),

    # do need to send across user_id - can get from jwt?  -
    # or other thing in header ?
]
