from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import ParameterAdminForm
from .models import (
    DataPoint, Parameter, Profile, UnitOption, ProfileParamUnitOption, User
)


class CustomUserAdmin(UserAdmin):
    # add_form = UserCreationForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2',
                       'is_temporary')}
         ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        UserAdmin.list_display = (
            'username', 'email', 'first_name', 'last_name', 'is_staff',
            'is_temporary'
        )


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
