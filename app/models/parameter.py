from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from .managers.parameter_manager import ParameterManager


class Parameter(models.Model):
    """ Built-in have admin level profile, rest are custom for a profile """

    name = models.CharField(
        max_length=50,
        help_text='e.g. Body weight',
    )
    upload_fields = models.CharField(
        max_length=100,
        choices=[('date, value', 'date, value'),
                 ('date, value, value2', 'date, value, value2')],
        verbose_name='csv upload field order string',
        help_text="Use comma separated field names e.g. 'date, value'"
    )
    upload_field_labels = models.CharField(
        max_length=100,
        help_text="For displaying upload_fields to users",
    )
    num_values = models.IntegerField(
        choices=[(1, '1'), (2, '2')],
        help_text='Indicates whether the DataPoint uses optional second value',
        default=1,
        verbose_name='Number of DataPoint values'
    )
    value2_short_label_1 = models.CharField(
        max_length=3,
        help_text="very short e.g. 3 letters, for 'value' display labels",
        null=True,
        blank=True
    )
    value2_short_label_2 = models.CharField(
        max_length=3,
        help_text="very short e.g. 3 letters, for 'value2' display labels",
        null=True,
        blank=True
    )
    ideal_info = models.CharField(
        max_length=160,
        default='',
        blank=True
    )
    ideal_info_url = models.CharField(
        max_length=240,
        default='',
        blank=True
    )
    is_builtin = models.BooleanField(
        default=False,
        help_text="Denotes if is non-custom/built-in metric for tracking"
    )
    profile = models.ForeignKey(
        'app.Profile',
        on_delete=models.CASCADE,
        related_name='custom_parameters',
    )
    custom_symbol = models.CharField(
        max_length=8,
        default='',
        blank=True
    )
    objects = ParameterManager()

    class Meta:
        unique_together = ('name', 'profile')

    @property
    def available_unit_options(self):
        return [{s: getattr(unit_choice, s) for s in
                 ['name', 'symbol', 'conversion_factor']}
                for unit_choice in self.unit_choices.all()]

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'Parameter: {self.name}'

    def save(self, **kwargs):
        upload_fields_len = len(self.upload_field_labels.split(', '))
        upload_fields_len_ne = len(self.upload_fields.split(', ')
                                   ) != upload_fields_len
        if upload_fields_len_ne or upload_fields_len < 2:
            raise ValidationError('fields should equal and upload_field_labels'
                                  ' needs gt 1 item')
        if upload_fields_len != self.num_values + 1:
            raise ValidationError('split upload_field_labels and '
                                  'num_values + 1 do not match up')
        super(Parameter, self).save(**kwargs)

    @classmethod
    def create_custom_metric(cls, profile, param_name, unit_symbol):
        # Validate param_name and return error message if necessary
        if cls.objects.filter(Q(metic_name=param_name) | Q(
                profile=profile, custom_param_name=param_name)).all():
            return False, 'Parameter name already exists'

    date_fmt_opts_map = dict(zip(
        ['YYYY/MM/DD', 'YYYY-MM-DD', 'YY/MM/DD', 'YY-MM-DD',
         'DD/MM/YYYY', 'DD-MM-YYYY', 'DD/MM/YY', 'DD-MM-YY'],
        ['%Y/%m/%d', '%Y-%m-%d', '%y/%m/%d', '%y-%m-%d',
         '%d/%m/%Y', '%d-%m-%Y', '%d/%m/%y', '%d-%m-%y']
    ))

