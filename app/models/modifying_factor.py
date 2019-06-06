# from django.db import models
#
#
# class ModifyingFactor(models.Model):
#     """ Model used by account for factors which may make a data unduly high or low when analysing as a trend
#        e.g. full of water/dehydrated when body weight,  """
#
#     name = models.CharField(
#         max_length=50,
#         verbose_name='Measurement value'
#     )
#     value = models.FloatField(
#         max_length=5,
#         # if time then make this have some fixed value - i.e. use default mod factor 10am -5% b.p  8pm +5% bp
#     )
#     time = models.TimeField(
#         verbose_name='Time of Day',
#         null=True,
#         blank=True,
#     )
#
#
#     # objects = SubTopicManager()
#
#     def __str__(self):
#         return 'foo'
#         # return f'{self.profile} {self.parameter} at {self.date}'
