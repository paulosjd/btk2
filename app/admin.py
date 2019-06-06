from django.contrib import admin

# from .forms.admin import ActivityAdminForm, BioactiveAdminForm, SubstructureAdminForm
from .models import (DataPoint, Parameter, Profile, UnitOption, )


@admin.register(DataPoint)
class DataPointAdmin(admin.ModelAdmin):
    pass


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    pass


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(UnitOption)
class UnitOptionAdmin(admin.ModelAdmin):
    pass

#
# @admin.register(Enzyme)
# class EnzymeAdmin(admin.ModelAdmin):
#
#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         if db_field.name == "mechanism":
#             kwargs["queryset"] = Activity.objects.order_by('category', 'name')
#         return super(EnzymeAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
#
# @admin.register(DataPoint)
# class ActivityAdmin(admin.ModelAdmin):
#     form = ActivityAdminForm
#
#     def get_queryset(self, request):
#         qs = super(ActivityAdmin, self).get_queryset(request)
#         return qs.order_by('action__name', 'name')
#
#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         if db_field.name == "action":
#             kwargs["queryset"] = Activity.objects.filter(category=1).order_by('action__name', 'name')
#         return super(ActivityAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
#
#
# @admin.register(Bioactive)
# class BioactiveAdmin(admin.ModelAdmin):
#     form = BioactiveAdminForm
#
#     def get_readonly_fields(self, request, obj=None):
#         if obj:  # editing an existing object
#             return self.readonly_fields + ('chemical_properties', 'iupac_name', 'smiles')
#         return self.readonly_fields
#
#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         if db_field.name == "activity":
#             kwargs["queryset"] = Activity.objects.order_by('category', 'name')
#         return super(BioactiveAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
#
#
# @admin.register(BioactiveCore)
# class BioactiveCoreAdmin(admin.ModelAdmin):
#
#     def get_readonly_fields(self, request, obj=None):
#         if obj:  # editing an existing object
#             return self.readonly_fields + ('cid_number', 'iupac_name', )
#         return self.readonly_fields
#
#
# @admin.register(CompanyPipeline)
# class CompanyPipelineAdmin(admin.ModelAdmin):
#     pass
#
#
# @admin.register(Development)
# class DevelopmentAdmin(admin.ModelAdmin):
#
#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         if db_field.name == "bioactive":
#             kwargs["queryset"] = Bioactive.objects.filter(development__isnull=True)
#         elif db_field.name == "activity":
#             kwargs["queryset"] = Activity.objects.order_by('category', 'name')
#         return super(DevelopmentAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
#
#
# @admin.register(Odorant)
# class OdorantAdmin(admin.ModelAdmin):
#
#     def get_readonly_fields(self, request, obj=None):
#         if obj:  # editing an existing object
#             return self.readonly_fields + ('cas_number', 'chemical_properties', 'iupac_name', 'smiles')
#         return self.readonly_fields
#