from django.test import TestCase

class FakeTestCase(TestCase):

    def test_fake_method(self):
        self.assertEqual(True, True)
