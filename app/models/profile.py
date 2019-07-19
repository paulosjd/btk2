from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from app.tasks.user_auth import send_verification_email


class Profile(models.Model):
    """ A model representing a User and their activity """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )
    email_confirmed = models.BooleanField(
        default=False,
    )
    birth_year = models.IntegerField(
        default=0,
    )
    gender = models.CharField(
        choices=[('', ' '), ('m', 'Male'), ('f', 'Female')],
        default='',
        max_length=1
    )
    # param_unit_option = models.ManyToManyField(
    #     'compounds.UnitOption',
    #     related_name='param_unit_options',
    #     blank=True,
    #     null=True,
    # )

    def __str__(self):
        return self.user.email + '_profile'

    def summary_data(self):
        return self.user_datapoints.order_by(
            'parameter', '-date').distinct('parameter')


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """ Creates a Profile instance when a User instance is created """
    if created:
        Profile.objects.create(user=instance)
        send_verification_email.delay(instance.pk)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """ Updates a Profile instance when a User instance is updated """
    instance.profile.save()
