from django.db import models


class UnitOptionQuerySet(models.QuerySet):
    pass


class UnitOptionManager(models.Manager):

    def get_queryset(self, is_builtin=True):
        if is_builtin:
            return self.unfiltered().filter(is_builtin=True)
        return self.unfiltered()

    def unfiltered(self):
        return UnitOptionQuerySet(
            self.model, using=self._db
        ).all()
