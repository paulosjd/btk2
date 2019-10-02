from django.contrib import admin

from .forms import (
    CustomParameterFilter, CustomParameterUnitsFilter, CustomUserAdmin,
    DatapointParamFilter, ParameterAdminForm, ProfileParamUnitOptionFilter,
    UnitOptionAdminForm,
)
from .models import (
    Bookmark, DataPoint, Parameter, Profile, ProfileParamUnitOption, UnitOption,
    User
)

admin.site.register(User, CustomUserAdmin)


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    pass


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
    param_profile = None
    param_is_custom = False
    form = UnitOptionAdminForm
    list_filter = [CustomParameterUnitsFilter]

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.param_profile = obj.parameter.profile
            self.param_is_custom = not obj.is_builtin
        return super(UnitOptionAdmin, self).get_form(request, obj, **kwargs)

    def get_queryset(self, request):
        if request.GET:
            return self.model.objects.unfiltered().all()
        return self.model.objects.all()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'parameter' and self.param_is_custom:
            kwargs["queryset"] = Parameter.objects.unfiltered().filter(
                profile=self.param_profile).all()
        return super(UnitOptionAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs)
