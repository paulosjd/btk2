from django.contrib import admin

from app.models import (
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


class CustomParameterFilter(admin.SimpleListFilter):
    title = 'Custom Parameters'
    parameter_name = 'id'

    def lookups(self, request, model_admin):
        return [(a.id, a.user.username) for a in
                Profile.objects.order_by('user__username').distinct()]

    def queryset(self, request, queryset):
        if self.value():
            queryset = Parameter.objects.custom_parameters().filter(
                profile=self.value())
        return queryset.all()


class CustomParameterUnitsFilter(admin.SimpleListFilter):
    title = 'Unit options for a profiles custom parameters'
    parameter_name = 'id'

    def lookups(self, request, model_admin):
        return [(a.id, a.user.username) for a in
                Profile.objects.order_by('user__username').distinct()]

    def queryset(self, request, queryset):
        if self.value():
            queryset = UnitOption.objects.unfiltered().filter(
                parameter__profile=self.value()).all()
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
