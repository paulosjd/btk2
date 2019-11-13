from django.core.exceptions import ValidationError
from django.db import models, DataError, IntegrityError
from django.db.models import Q

from app.models.managers.parameter_manager import ParameterManager


class Parameter(models.Model):
    """ Built-in have admin level profile, rest are custom for a profile """

    name = models.CharField(
        max_length=50,
        help_text='e.g. Body weight',
    )
    upload_fields = models.CharField(
        max_length=100,
        default='date, value',
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
        help_text='Whether ',
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
        help_text="Indicates if admin level or user custom level"
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
    def available_parameters_for_profile(cls, profile):
        return cls.objects.union(
            cls.objects.custom_parameters().filter(profile=profile)
        ).all()

    @classmethod
    def create_custom_metric(cls, profile, param_name, unit_symbol):
        """
        :param profile: Profile instance
        :param param_name: str used for 'name' value
        :param unit_symbol: str used for 'custom_field' value
        :return: Tuple of Parameter instance or False and str message for user
        """
        if cls.objects.unfiltered().filter(
                Q(name=param_name, is_builtin=True) |
                Q(name=param_name, profile=profile)
        ).all():
            return False, 'Name already exists'
        try:
            instance = cls.objects.create(
                name=param_name, profile=profile, custom_symbol=unit_symbol,
                upload_field_labels=f'date, {param_name} measurements',
                is_builtin=False
            )
        except (DataError, IntegrityError):
            return False, 'Invalid data'
        return instance, ''

    date_formats = ['YYYY/MM/DD', 'YYYY-MM-DD', 'YY/MM/DD', 'YY-MM-DD',
                    'DD/MM/YYYY', 'DD-MM-YYYY', 'DD/MM/YY', 'DD-MM-YY']

    date_fmt_opts_map = dict(zip(
        date_formats,
        ['%Y/%m/%d', '%Y-%m-%d', '%y/%m/%d', '%y-%m-%d',
         '%d/%m/%Y', '%d-%m-%Y', '%d/%m/%y', '%d-%m-%y']
    ))
