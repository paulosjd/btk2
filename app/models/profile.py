from datetime import datetime

from django.db import models

from .parameter import Parameter
from .user import User


class Profile(models.Model):
    """ A model representing a User and their activity """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )
    email_confirmed = models.BooleanField(
        default=False,
    )
    birth_year = models.IntegerField(
        default=0,
    )
    height = models.IntegerField(
        default=0,
        help_text='Height in cm'
    )
    gender = models.CharField(
        choices=[('', ' '), ('m', 'Male'), ('f', 'Female')],
        default='',
        max_length=1
    )

    @property
    def age(self):
        if self.birth_year:
            return datetime.now().year - self.birth_year

    def __str__(self):
        return self.user.username + '_profile'

    def available_parameters(self):
        return Parameter.objects.union(
            Parameter.objects.custom_parameters().filter(profile=self))

    def available_unit(self):
        return Parameter.objects.union(
            Parameter.objects.custom_parameters().filter(profile=self))

    def all_datapoints(self):
        return self.user_datapoints.order_by(
            'parameter', '-date').all()

    def summary_data(self):
        return self.user_datapoints.order_by(
            'parameter', '-date').distinct('parameter')

    def param_unit_options(self):
        return self.unit_options.order_by(
            'parameter').distinct('parameter')

    def all_bookmarks(self):
        return self.user_datapoints.order_by(
            'parameter', '-date').all()


    @classmethod
    def create_demo_user(cls):
        cls.objects.create(is_temporary=True)


