from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from app.models import DataPoint, Profile, ProfileParamUnitOption, UnitOption
from app.tasks.user_admin import send_verification_email
from btk2 import settings


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """ Creates a Profile instance when a User instance is created """
    if created:
        profile = Profile.objects.create(user=instance)
        if getattr(instance, 'is_temporary', ''):
            create_temp_profile_data(profile)
        else:
            send_verification_email.delay(instance.pk)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    """ Updates a Profile instance when a User instance is updated """
    instance.profile.save()


def create_temp_profile_data(profile):
    demo_profile = Profile.objects.get(user__username='demo')
    for field in ['birth_year', 'height', 'gender']:
        setattr(profile, field, getattr(demo_profile, field))
    profile.save()
    user_dps = demo_profile.user_datapoints.all()
    prof_pms = demo_profile.profile_parameters.all()

    for qs, model in [(user_dps, DataPoint),
                      (prof_pms, ProfileParamUnitOption)]:
        copies = []
        for obj in qs:
            obj.pk = None
            obj.profile = profile
            copies.append(obj)
        model.objects.bulk_create(copies)


@receiver(post_save, sender=UnitOption)
def create_profile_param_unit_option(sender, instance, created, **kwargs):
    """ Creates a UnitOption instance when a Parameter instance is created """
    if created and not instance.is_builtin:
        ProfileParamUnitOption.objects.create(
            parameter=instance.parameter, profile=instance.parameter.profile,
            unit_option=instance
        )


@receiver(post_delete)
def profile_param_unit_option_post_delete(sender, instance, *args, **kwargs):
    """ To clean up data. Note that as sender argument not included in the
    decorator, this callback is called for all models """
    if sender == DataPoint:
        filter_kwargs = dict(profile=instance.profile,
                             parameter=instance.parameter)
        if not DataPoint.objects.filter(**filter_kwargs).exists():
            for obj in ProfileParamUnitOption.objects.filter(**filter_kwargs):
                obj.delete()
