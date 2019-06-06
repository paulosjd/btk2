from django.db import models


class ParameterQuerySet(models.QuerySet):

    pass
    # def medicinal(self):
    #     return self.filter(category=1)
    #
    # def food(self):
    #     return self.filter(category=2)


class ParameterManager(models.Manager):

    def get_queryset(self):
        return ParameterQuerySet(self.model, using=self._db).all()
        # return ParameterQuerySet(self.model, using=self._db).prefetch_related('modifying_factor')


    # def medicinal(self):
    #     return self.get_queryset().medicinal()
    #
    # def food(self):
    #     return self.get_queryset().food()
