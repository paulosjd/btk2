from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import ParameterAdminForm
from .models import (
    DataPoint, Parameter, Profile, UnitOption, ProfileParamUnitOption, User
)


class DatapointParamFilter(admin.SimpleListFilter):
    title = 'Parameter (by Profile="dev")'
    parameter_name = 'id'

    def lookups(self, request, model_admin):
        return [(a.id, a.name) for a in
                Parameter.objects.order_by('name').distinct()]

    def queryset(self, request, queryset):
        if self.value():
            profile = Profile.objects.filter(user__username='dev').first()
            return queryset.filter(parameter__id=self.value(),
                                   profile=profile)
        return queryset.all()


class ProfileParamUnitOptionFilter(admin.SimpleListFilter):
    title = 'Unit Option (by Profile="dev")'
    parameter_name = 'id'

    def lookups(self, request, model_admin):
        return [(a.id, a.name) for a in
                UnitOption.objects.order_by('symbol').distinct()]

    def queryset(self, request, queryset):
        if self.value():
            profile = Profile.objects.filter(user__username='dev').first()
            return queryset.filter(unit_option__id=self.value(),
                                   profile=profile)
        return queryset.all()


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
    list_filter = [DatapointParamFilter]


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    form = ParameterAdminForm


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(ProfileParamUnitOption)
class ProfileParamUnitOptionAdmin(admin.ModelAdmin):
    list_filter = [ProfileParamUnitOptionFilter]


@admin.register(UnitOption)
class UnitOptionAdmin(admin.ModelAdmin):
    pass
