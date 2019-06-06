from django.urls import path

from .views.csv_upload import CsvUpload
from app.views.user.create_user import CreateUserView
from .views.profile_summary import ProfileSummary


urlpatterns = [
    path('test', CsvUpload.as_view(), name='csv-upload'),
    path('user/register', CreateUserView.as_view(), name='register'),
    path('profile/<int:user_id>/summary', ProfileSummary.as_view())
    # do need to send across user_id - can get from jwt?  -
    # or other thing in header ?
]
