from django.db.models.signals import post_save
from django.dispatch import receiver

from app.models import DataPoint, Profile, ProfileParamUnitOption
from app.tasks.user_registration import send_verification_email
from btk2 import settings


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """ Creates a Profile instance when a User instance is created """
    if created:
        profile = Profile.objects.create(user=instance)
        send_verification_email.delay(instance.pk)

        if getattr(instance, 'is_temporary', ''):
            create_temp_profile_data(profile)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    """ Updates a Profile instance when a User instance is updated """
    instance.profile.save()


def create_temp_profile_data(profile):
    demo_profile = Profile.objects.get(user__username='demo')

    copies = []
    for obj in demo_profile.user_datapoints.all():
        obj.pk = None
        obj.profile = profile
        copies.append(obj)
    DataPoint.objects.bulk_create(copies)

    copies = []
    for obj in demo_profile.profile_parameters.all():
        obj.pk = None
        obj.profile = profile
        copies.append(obj)
    ProfileParamUnitOption.objects.bulk_create(copies)
