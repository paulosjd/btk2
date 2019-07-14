from django.db import models


class DatapointManager(models.Manager):

    def get_queryset(self):
        return super(DatapointManager, self).get_queryset()
