from django.urls import path

from .views.profile import (
    MenuItemAdd, ProfileInfoUpdate, ProfileSummaryData,
)
from app.views.data_point.add_data_points import AddDataPoints
from app.views.data_point.edit_data_points import EditDataPoints
from app.views.data_point.qualifying_text import QualifyingTextCrudView
from .views.csv_download import CsvDownloadView
from .views.csv_upload import CsvUploadView
from .views.user import (
    LoginHelp, PasswordReset, RegistrationAPIView, DemoRegistrationAPIView
)

urlpatterns = [
    path('users/demo/registration', DemoRegistrationAPIView.as_view()),
    path('users/registration', RegistrationAPIView.as_view()),
    path('users/help/<forgot>', LoginHelp.as_view()),
    path('users/password-reset', PasswordReset.as_view()),

    path('profile/summary', ProfileSummaryData.as_view()),
    path('profile/menu-item-add', MenuItemAdd.as_view()),
    path('profile/info-update', ProfileInfoUpdate.as_view()),
    path('datapoints/add', AddDataPoints.as_view()),
    path('datapoints/edit', EditDataPoints.as_view()),
    path('datapoints/qualifying-text', QualifyingTextCrudView.as_view()),
    path('datapoints/download', CsvDownloadView.as_view()),
    path('datapoints/upload', CsvUploadView.as_view()),

    # do need to send across user_id - can get from jwt?  -
    # or other thing in header ?
]
