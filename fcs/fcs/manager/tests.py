from django.test import TestCase
from fcs.fcs.manager.models import FakeModel

class FakeModelTest(TestCase):
    test_obj = None

    def setUp(self):
        self.__class__.test_obj = FakeModel()

    def fake_method_test(self):
        self.assertEqual(self.__class__.test_obj.fake_method(), True)

