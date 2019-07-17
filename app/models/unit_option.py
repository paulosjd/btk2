from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from .parameter import Parameter


class UnitOption(models.Model):
    """ Represents a non-default unit of measurement for a parameter, e.g. lb for body mass """
    name = models.CharField(
        max_length=100,
        help_text='Label e.g. pounds'
    )
    symbol = models.CharField(
        max_length=8,
        help_text='Label e.g. lb'
    )
    conversion_factor = models.FloatField(
        max_length=10,
        help_text='Enables conversion to and from the default unit of measurement; can be negative'
    )
    param_default = models.BooleanField(
        default=False,
    )
    parameter = models.ForeignKey(
        Parameter,
        related_name='unit_choices',
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = ('parameter', 'symbol',)
        ordering = ('-param_default', 'name', )

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'Unit Option: {self.name}'

    def save(self, *args, **kwargs):
        if self.param_default:
            try:
                unit_opt = UnitOption.objects.get(param_default=True, parameter=self.parameter)
                unit_opt.param_default = False
                unit_opt.save()
            except UnitOption.DoesNotExist:
                self.param_default = True
        super(UnitOption, self).save(*args, **kwargs)

    @classmethod
    def get_default_for_param(cls, parameter):
        return cls.objects.get(parameter=parameter, param_default=True)


@receiver(post_save, sender=Parameter)
def create_user_profile(sender, instance, created, **kwargs):
    """ Creates a Profile instance when a User instance is created """
    if created:
        UnitOption.objects.create(
            name=instance.default_unit_name,
            symbol=instance.default_unit_symbol,
            conversion_factor=1,
            param_default=True,
            parameter=instance
        )
