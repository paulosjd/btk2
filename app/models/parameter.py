from django.db import models
from django.core.exceptions import ValidationError

from .managers.parameter_manager import ParameterManager


class Parameter(models.Model):

    date_fmt_opts_map = dict(zip(
        ['YYYY/MM/DD', 'YYYY-MM-DD', 'YY/MM/DD', 'YY-MM-DD', 'DD/MM/YYYY', 'DD-MM-YYYY', 'DD/MM/YY', 'DD-MM-YY'],
        ['%Y/%m/%d', '%Y-%m-%d', '%y/%m/%d', '%y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%d/%m/%y', '%d-%m-%y']
    ))

    name = models.CharField(
        max_length=50,
        help_text='e.g. Body weight'
    )

    # modifying_factor = models.ForeignKey(
    #     'app.ModifyingFactor',
    #     help_text='Information to compensate e.g. time taken bp g ... so that on trend line can factor out slightly',
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
    upload_fields = models.CharField(
        max_length=100,
        verbose_name='csv upload field order string',
        help_text="Use comma separated field names e.g. 'date, value'"

    )
    upload_field_labels = models.CharField(
        max_length=100,
        help_text="Allows mapping of descriptive names to the model fields 'value' and 'value2'. E.g. mapping the "
                  "names 'systolic' and 'diastolic' to these fields for a model instance representing blood pressure",
        default=''
    )

    objects = ParameterManager()

    def __str__(self):
        return f'Parameter: {self.name}'

    def save(self, **kwargs):
        if len(self.upload_fields.split(', ')) != len(self.upload_field_labels.split(', ')):
            raise ValidationError('fields should equal')
        super(Parameter, self).save(**kwargs)
