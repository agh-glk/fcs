from django.test import TestCase
from models import FakeModel, UserData, Quota, User, QuotaException, Task
from datetime import datetime

class FakeModelTest(TestCase):
    test_obj = None

    def setUp(self):
        self.__class__.test_obj = FakeModel()

    def fake_method_test(self):
        self.assertEqual(self.__class__.test_obj.fake_method(), True)


class TaskModelTest(TestCase):

    def setUp(self):
        user = User.objects.create_user(username='test_user', password='test_pwd', email='test@gmail.pl')
        quota = Quota.objects.create(max_priority=10, user=user)
        quota.save()
        user_data = UserData.objects.create(user=user)
        user_data.save()
        self.client = user

    def successful_task_creation_test(self):
        task = None
        try:
            task = Task.create_task(self.client, 'Task1', 3, datetime.now(), 'text', 'onet.pl', max_links=400)
            self.assertEqual(1,len(Task.objects.all()))
        except QuotaException:
            self.fail('Exception occured')
        finally:
            if task:
                task.delete()

    def failed_task_creation_test(self):
        self.assertRaisesMessage(QuotaException, 'Task priority exceeds user quota!', Task.create_task, self.client, 'Task1',
                                 15, datetime.now(), 'text', 'onet.pl', max_links=400)

    def tearDown(self):
        self.client.delete()
