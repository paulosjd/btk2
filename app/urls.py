from django.urls import path

from app.views.data_point.csv_download import CsvDownloadView
from app.views.data_point.csv_upload import CsvUploadView
from .views.data_point.add_data_points import AddDataPoints
from .views.data_point.edit_data_points import EditDataPoints
from .views.data_point.qualifying_text import QualifyingTextCrudView
from .views.profile import (
    AddBookmarksView, CustomMetricAdd, EditBookmarksView, LinkedParamCrud,
    MenuItemAdd, ParamColorsUpdateView, ProfileInfoUpdate, ProfileSummaryData,
    TargetUpdateView,
)
from .views.user import (
    DeleteUserView, DemoRegistrationAPIView, EmailEditView, LoginHelp,
    PasswordReset, RegistrationAPIView, NewVerificationEmail
)


urlpatterns = [
    path('datapoints/add', AddDataPoints.as_view()),
    path('datapoints/download', CsvDownloadView.as_view()),
    path('datapoints/edit', EditDataPoints.as_view()),
    path('datapoints/qualifying-text', QualifyingTextCrudView.as_view()),
    path('datapoints/upload', CsvUploadView.as_view()),

    path('profile/bookmarks-add', AddBookmarksView.as_view()),
    path('profile/bookmarks-edit', EditBookmarksView.as_view()),
    path('profile/custom-metric-add', CustomMetricAdd.as_view()),
    path('profile/info-update', ProfileInfoUpdate.as_view()),
    path('profile/menu-item-add', MenuItemAdd.as_view()),
    path('profile/linked-param/<action>', LinkedParamCrud.as_view()),
    path('profile/param-colors', ParamColorsUpdateView.as_view()),
    path('profile/summary', ProfileSummaryData.as_view(), name='summary'),
    path('profile/target-update', TargetUpdateView.as_view()),

    path('users/confirm-delete', DeleteUserView.as_view()),
    path('users/demo/registration', DemoRegistrationAPIView.as_view()),
    path('users/email/edit', EmailEditView.as_view()),
    path('users/help/<forgot>', LoginHelp.as_view()),
    path('users/new-verification-email', NewVerificationEmail.as_view()),
    path('users/password-reset', PasswordReset.as_view()),
    path('users/registration', RegistrationAPIView.as_view()),
]
