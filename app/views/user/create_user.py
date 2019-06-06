from django.contrib.auth.models import User
from rest_framework import permissions
from rest_framework.generics import CreateAPIView

from app.serializers import UserSerializer


class CreateUserView(CreateAPIView):

    model = User
    permission_classes = [
        permissions.AllowAny # Or anon users can't register
    ]
    serializer_class = UserSerializer
