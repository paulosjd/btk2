from django.db import models


class ParameterQuerySet(models.QuerySet):
    pass


class ParameterManager(models.Manager):

    def get_queryset(self, is_builtin=True):
        if is_builtin:
            return self.unfiltered().filter(is_builtin=True)
        return self.unfiltered()

    def unfiltered(self):
        return ParameterQuerySet(
            self.model, using=self._db
        ).all()

    def custom_parameters(self):
        return self.get_queryset(is_builtin=False)
