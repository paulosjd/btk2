# import logging
# from collections import namedtuple
#
# from django.core.exceptions import ObjectDoesNotExist, ValidationError
# from django.db import IntegrityError, models
#
# log = logging.getLogger(__name__)
#
#
# class Intervention(models.Model):
#
#     value = models.FloatField(
#         max_length=5,
#     )
#     start_date = models.DateField(
#         help_text='Date of measurement'
#     )
#     end_date = models.DateField(
#         help_text='Date of measurement',
#         null=True,
#         blank=True
#     )
#     parameter = models.ForeignKey(
#         'app.Parameter',
#         on_delete=models.CASCADE,
#         related_name='parameters',
#     )
#     profile = models.ForeignKey(
#         'app.Profile',
#         on_delete=models.CASCADE,
#         related_name='user_datapoints',
#     )
#
#     class Meta:
#         unique_together = ('date', 'parameter', 'profile')
#         ordering = ('date', )
#
#     def __str__(self):
#         return f'{self.profile} {self.parameter} at {self.date}'
#
#     # def save(self, *args, **kwargs):
#     #     if not all([self.profile, self.parameter]):
#     #         raise IntegrityError
#     #     try:
#     #         ProfileParamUnitOption.get_unit_option(self.profile, self.parameter)
#     #     except ObjectDoesNotExist as e:
#     #         log.error(e)
#     #         raise ValidationError('ProfileParamUnitOption does not exist')
#     #     super(DataPoint, self).save(*args, **kwargs)
