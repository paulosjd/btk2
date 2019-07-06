from django.db import models


class ProfileQuerySet(models.QuerySet):

    pass
    # def medicinal(self):
    #     return self.filter(category=1)
    #
    # def food(self):
    #     return self.filter(category=2)


class ProfileManager(models.Manager):

    def get_queryset(self):
        return ProfileQuerySet(self.model, using=self._db).all()
        # return ParameterQuerySet(self.model, using=self._db).prefetch_related('modifying_factor')

    #
    # def food(self):
    #     return self.get_queryset().food()
