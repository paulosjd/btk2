from django.db import models

from .managers.parameter_manager import ParameterManager


class Parameter(models.Model):

    name = models.CharField(
        max_length=50,
        help_text='e.g. Body weight'
    )
    # other ways to characterize modifying effects - e.g. time of day
    #
    # modifying_factor = models.ForeignKey(
    #     'app.ModifyingFactor',
    #     help_text='Information to compensate e.g. time taken bp late morning ... so that on trend line can factor out slightly',
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    # )
    # date_time  ... so use this to give modifying_factor a fixed value using time, in certain cases, e.g.
    # enter a BP and is mid morning -5% whereas at 9pm +5%

    default_unit_name = models.CharField(
        max_length=100,
        help_text='Label e.g. kilograms'
    )
    default_unit_symbol = models.CharField(
        max_length=8,
        help_text='Label e.g. kg'
    )

    objects = ParameterManager()

    def __str__(self):
        return f'Parameter: {self.name}'
