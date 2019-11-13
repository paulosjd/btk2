from django.test import TestCase

from app.models import Parameter, User


class BaseTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super(BaseTestCase, cls).setUpClass()
        user = User.objects.create(username='tester')
        user2 = User.objects.create(username='tester2')
        cls.profile_1 = user.profile
        cls.profile_2 = user2.profile
        cls.profile_2.birth_year = 1984
        param_extras = dict(upload_fields='date, value',
                            upload_field_labels='foo, bar')
        cls.param1 = Parameter.objects.create(
            name='p1name', profile=cls.profile_1, **param_extras
        )
        cls.param2 = Parameter.objects.create(
            name='p2name', profile=cls.profile_2, is_builtin=True,
            **param_extras,
        )
        cls.profile_param_unit_opt = cls.profile_1.profile_parameters.first()
        cls.profile_param_unit_opt.linked_parameter = cls.param2
        cls.profile_param_unit_opt.save()
