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

    def __str__(self):
        return self.user.email + '_profile'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """ Creates a Profile instance when a User instance is created """
    if created:
        # instance.email = f'{instance.username}_s@foo.com'
        # instance.save()
        Profile.objects.create(user=instance)
        send_verification_email.delay(instance.pk)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """ Updates a Profile instance when a User instance is updated """
    instance.profile.save()
