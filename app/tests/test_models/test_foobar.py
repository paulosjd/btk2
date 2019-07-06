import unittest
from unittest.mock import patch


from django.test import TestCase


class FooTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_smoke(self):
        self.assertEqual(4, 5)
