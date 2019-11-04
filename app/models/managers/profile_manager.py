from django.db import models


class ProfileQuerySet(models.QuerySet):

    def verified(self):
        return self.filter(email_confirmed=True)


class ProfileManager(models.Manager):

    def get_queryset(self):
        return ProfileQuerySet(self.model, using=self._db).all()

    def verified(self):
        return self.get_queryset().verified()
