from django.contrib import admin
from django.contrib.auth import views as auth
from django.urls import path, include

from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.views import refresh_jwt_token
from rest_framework_jwt.views import verify_jwt_token


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
    path('reset-password/complete/', auth.PasswordResetCompleteView.as_view(
        template_name='password_reset_complete.html'
    ), name='password_reset_complete', ),
]
