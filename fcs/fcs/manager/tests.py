from django.test import TestCase
from models import UserData, Quota, User, QuotaException, Task, CrawlingType, CRAWLING_TYPES_CHOICES
from django.utils import timezone


class TaskModelTest(TestCase):

    user = None

    def get_user(self):
        if self.user is None:
            self.user = User.objects.all()[0]
        return self.user

    @classmethod
    def setUpClass(cls):
        CrawlingType.objects.create(type=CrawlingType.TEXT).save()
        CrawlingType.objects.create(type=CrawlingType.LINKS).save()
        CrawlingType.objects.create(type=CrawlingType.PICTURES).save()
        _user = User.objects.create_user(username='test_user', password='test_pwd', email='test@gmail.pl')
        quota = Quota.objects.create(max_priority=10, max_tasks=1, max_links=1000, user=_user)
        quota.save()
        user_data = UserData.objects.create(user=_user)
        user_data.save()

    def test_successful_task_creation(self):
        task = None
        try:
            task = Task.create_task(self.get_user(), 'Task1', 3, timezone.now(),
                                    [CrawlingType.objects.get(type=CrawlingType.TEXT)], 'onet.pl', max_links=400)
            self.assertEqual(1, self.get_user().task_set.count())
        except QuotaException:
            self.fail('Exception occured')
        finally:
            if task:
                task.delete()

    def test_failed_task_creation(self):
        self.assertRaisesMessage(QuotaException, 'Task priority exceeds user quota!', Task.create_task, self.get_user(),
                                 'Task1', 15, timezone.now(),  [CrawlingType.objects.get(type=CrawlingType.TEXT)],
                                 'onet.pl', max_links=400)
        self.assertRaisesMessage(QuotaException, 'Task link limit exceeds user quota!', Task.create_task, self.get_user(),
                                 'Task1', 5, timezone.now(),  [CrawlingType.objects.get(type=CrawlingType.TEXT)],
                                 'onet.pl', max_links=1400)
        Task.create_task(self.get_user(), 'Task1', 5, timezone.now(), [CrawlingType.objects.get(type=CrawlingType.TEXT)],
                         'onet.pl', max_links=400)
        self.assertRaisesMessage(QuotaException, 'User has too many opened tasks!', Task.create_task, self.get_user(),
                                 'Task2', 5, timezone.now(), [CrawlingType.objects.get(type=CrawlingType.TEXT)],
                                 'onet.pl', max_links=400)

    def test_change_priority(self):
        task = Task.create_task(self.get_user(), 'Task1', 5, timezone.now(),
                                [CrawlingType.objects.get(type=CrawlingType.TEXT)], 'onet.pl', max_links=400)
        self.assertEqual(5,task.priority)
        task.change_priority(10)
        self.assertEqual(10,task.priority)
        self.assertRaisesMessage(QuotaException, 'Task priority exceeds user quota!', task.change_priority, 15)
        self.assertEqual(10,task.priority)

    def test_pause_and_resume(self):
        task = Task.create_task(self.get_user(), 'Task1', 5, timezone.now(),
                                [CrawlingType.objects.get(type=CrawlingType.TEXT)], 'onet.pl', max_links=400)
        self.assertEqual(True,task.active)
        task.pause()
        self.assertEqual(False,task.active)
        task.resume()
        self.assertEqual(True,task.active)

    def test_finish(self):
        task = Task.create_task(self.get_user(), 'Task1', 5, timezone.now(),
                                [CrawlingType.objects.get(type=CrawlingType.TEXT)], 'onet.pl', max_links=400)
        self.assertRaisesMessage(QuotaException, 'User has too many opened tasks!', Task.create_task, self.get_user(),
                                 'Task1', 5, timezone.now(), [CrawlingType.objects.get(type=CrawlingType.TEXT)],
                                 'onet.pl', max_links=400)
        task.stop()
        self.assertEqual(True, task.finished)
        Task.create_task(self.get_user(), 'Task2', 5, timezone.now(), [CrawlingType.objects.get(type=CrawlingType.TEXT)],
                         'onet.pl', max_links=400)

    def tearDown(self):
        self.get_user().delete()
