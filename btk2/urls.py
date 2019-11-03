from django.contrib import admin
from django.contrib.auth import views as auth
from django.urls import include, path, re_path
from rest_framework_jwt.views import (
    obtain_jwt_token, refresh_jwt_token, verify_jwt_token
)

from .activate import activate, PasswordResetIsCompleteView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('app.urls')),
    path('auth-jwt/', obtain_jwt_token),
    path('auth-jwt-refresh/', refresh_jwt_token),
    path('auth-jwt-verify/', verify_jwt_token),
    path('auth-jwt-refresh/', refresh_jwt_token),
    path('reset/<uidb64>/<token>/', auth.PasswordResetConfirmView.as_view(
        template_name='password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset-password/complete/', PasswordResetIsCompleteView.as_view(
        template_name='password_reset_complete.html'
    ), name='password_reset_complete', ),
    re_path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]'
            r'{1,13}-[0-9A-Za-z]{1,20})/$', activate, name='activate'),
]
