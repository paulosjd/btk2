from django.contrib import admin

from .forms import (
    CustomParameterFilter, CustomParameterUnitsFilter, CustomUserAdmin,
    DatapointParamFilter, ParameterAdminForm, ProfileParamUnitOptionFilter,
    UnitOptionAdminForm,
)
from .models import (
    DataPoint, Parameter, Profile, UnitOption, ProfileParamUnitOption, User
)

admin.site.register(User, CustomUserAdmin)


@admin.register(DataPoint)
class DataPointAdmin(admin.ModelAdmin):
    ordering = ('parameter', '-date')
    list_filter = [DatapointParamFilter]


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    form = ParameterAdminForm
    list_filter = [CustomParameterFilter]

    def get_queryset(self, request):
        if request.GET:
            return self.model.objects.unfiltered().all()
        return self.model.objects.all()


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(ProfileParamUnitOption)
class ProfileParamUnitOptionAdmin(admin.ModelAdmin):
    list_filter = [ProfileParamUnitOptionFilter]


@admin.register(UnitOption)
class UnitOptionAdmin(admin.ModelAdmin):
    form = UnitOptionAdminForm
    list_filter = [CustomParameterUnitsFilter]

    def get_queryset(self, request):
        if request.GET:
            return self.model.objects.unfiltered().all()
        return self.model.objects.all()
