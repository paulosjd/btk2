from django.db import models


class ProfileQuerySet(models.QuerySet):

    pass
    # def abc(self):
    #     return self.filter(category=1)


class ProfileManager(models.Manager):

    def get_queryset(self):
        return ProfileQuerySet(self.model, using=self._db).all()
