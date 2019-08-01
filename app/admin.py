from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .forms import ParameterAdminForm
from .models import (
    DataPoint, Parameter, Profile, UnitOption, ProfileParamUnitOption,
)


class CustomUserAdmin(UserAdmin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        UserAdmin.list_display = (
            'username', 'email', 'first_name', 'last_name', 'is_staff'
        )


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(DataPoint)
class DataPointAdmin(admin.ModelAdmin):
    ordering = ('parameter', '-date')


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    form = ParameterAdminForm


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(ProfileParamUnitOption)
class ProfileParamUnitOptionAdmin(admin.ModelAdmin):
    pass


@admin.register(UnitOption)
class UnitOptionAdmin(admin.ModelAdmin):
    pass
