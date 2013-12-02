from django.test import TestCase
from models import FakeModel, UserData, Quota, User, QuotaException, Task
from django.utils import timezone

class FakeModelTest(TestCase):
    test_obj = None

    def setUp(self):
        self.__class__.test_obj = FakeModel()

    def fake_method_test(self):
        self.assertEqual(self.__class__.test_obj.fake_method(), True)


class TaskModelTest(TestCase):

    def setUp(self):
        user = User.objects.create_user(username='test_user', password='test_pwd', email='test@gmail.pl')
        quota = Quota.objects.create(max_priority=10, max_tasks=1, max_links=1000, user=user)
        quota.save()
        user_data = UserData.objects.create(user=user)
        user_data.save()
        self.client = user

    def test_successful_task_creation(self):
        task = None
        try:
            task = Task.create_task(self.client, 'Task1', 3, timezone.now(), 'text', 'onet.pl', max_links=400)
            self.assertEqual(1,self.client.task_set.count())
        except QuotaException:
            self.fail('Exception occured')
        finally:
            if task:
                task.delete()

    def test_failed_task_creation(self):
        self.assertRaisesMessage(QuotaException, 'Task priority exceeds user quota!', Task.create_task, self.client, 'Task1',
                                 15, timezone.now(), 'text', 'onet.pl', max_links=400)
        self.assertRaisesMessage(QuotaException, 'Task link limit exceeds user quota!', Task.create_task, self.client, 'Task1',
                                 5, timezone.now(), 'text', 'onet.pl', max_links=1400)
        Task.create_task(self.client, 'Task1', 5, timezone.now(), 'text', 'onet.pl', max_links=400)
        self.assertRaisesMessage(QuotaException, 'User has too many opened tasks!', Task.create_task, self.client, 'Task2',
                                 5, timezone.now(), 'text', 'onet.pl', max_links=400)

    def test_change_priority(self):
        task = Task.create_task(self.client, 'Task1', 5, timezone.now(), 'text', 'onet.pl', max_links=400)
        self.assertEqual(5,task.priority)
        task.change_priority(10)
        self.assertEqual(10,task.priority)
        self.assertRaisesMessage(QuotaException, 'Task priority exceeds user quota!', task.change_priority, 15)
        self.assertEqual(10,task.priority)

    def test_pause_and_resume(self):
        task = Task.create_task(self.client, 'Task1', 5, timezone.now(), 'text', 'onet.pl', max_links=400)
        self.assertEqual(True,task.active)
        task.pause()
        self.assertEqual(False,task.active)
        task.resume()
        self.assertEqual(True,task.active)

    def test_finish(self):
        task = Task.create_task(self.client, 'Task1', 5, timezone.now(), 'text', 'onet.pl', max_links=400)
        self.assertRaisesMessage(QuotaException, 'User has too many opened tasks!', Task.create_task, self.client, 'Task1',
                                 5, timezone.now(), 'text', 'onet.pl', max_links=400)
        task.finish()
        self.assertEqual(True,task.finished)
        Task.create_task(self.client, 'Task2', 5, timezone.now(), 'text', 'onet.pl', max_links=400)

    def tearDown(self):
        self.client.delete()
