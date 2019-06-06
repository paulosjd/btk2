from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


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
        return self.user.username + '_profile'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Creates an instance when a User instance is created
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Updates an instance when a User instance is updated
    """
    instance.profile.save()


@receiver(post_save, sender=User)
def send_verification_email(sender, instance, signal, *args, **kwargs):
    if not instance.profile.email_confirmed:
        # Send verification email
        send_mail(
            'Follow this link to verify your account: '
            'http://localhost:8000'  # % reverse('verify', kwargs={
                # from: 'uuid': str(instance.verification_uuid)
                #}),
            'from@foo.dev',
            [instance.email],
            fail_silently=False,
        )
