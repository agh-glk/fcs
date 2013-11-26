from django.test import TestCase
from models import FakeModel

class FakeModelTestCase(TestCase):
    test_obj = None

    def setUp(self):
        self.__class__.test_obj = FakeModel()

    def test_fake_method(self):
        self.assertEqual(self.__class__.test_obj.fake_method(), True)

