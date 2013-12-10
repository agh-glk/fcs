from models import UserData, Quota, User, QuotaException, Task, CrawlingType
from django.utils import timezone
from django_pytest.conftest import pytest_funcarg__client, pytest_funcarg__django_client

class TestTask:
    def get_user(self):
        if self.user is None:
            self.user = User.objects.get(username='test_user5')
        return self.user

    def setup(self):
        self.user = User.objects.create_user(username='test_user5', password='test_pwd', email='test@gmail.pl')
        CrawlingType.objects.create(type=CrawlingType.TEXT)
        CrawlingType.objects.create(type=CrawlingType.LINKS)
        CrawlingType.objects.create(type=CrawlingType.PICTURES)
        Quota.objects.create(max_priority=10, max_tasks=1, max_links=1000, user=self.user)
        UserData.objects.create(user=self.user)

    def teardown(self):
        self.user.delete()
        CrawlingType.objects.all().delete()

    def test_successful_task_creation(self):
        Task.create_task(self.get_user(), 'Task1', 3, timezone.now(),
                                [CrawlingType.objects.get(type=CrawlingType.TEXT)], 'onet.pl', max_links=400)
        assert self.get_user().task_set.count() == 1, 'Task was not properly saved!'

    def test_failed_task_creation(self):
        try:
            Task.create_task(self.get_user(), 'Task1', 15, timezone.now(),
                             [CrawlingType.objects.get(type=CrawlingType.TEXT)], 'onet.pl', max_links=400)
            assert False, 'Exception should be raised!'
        except QuotaException as e:
            assert e.message == 'Task priority exceeds user quota!', 'Wrong exception message!'

        try:
            Task.create_task(self.get_user(), 'Task1', 5, timezone.now(),
                             [CrawlingType.objects.get(type=CrawlingType.TEXT)], 'onet.pl', max_links=1400)
            assert False, 'Exception should be raised!'
        except QuotaException as e:
            assert e.message == 'Task link limit exceeds user quota!', 'Wrong exception message!'

        try:
            Task.create_task(self.get_user(), 'Task1', 5, timezone.now(),
                             [CrawlingType.objects.get(type=CrawlingType.TEXT)], 'onet.pl', max_links=400)
            Task.create_task(self.get_user(), 'Task2', 5, timezone.now(),
                             [CrawlingType.objects.get(type=CrawlingType.TEXT)], 'onet.pl', max_links=400)
            assert False, 'Exception should be raised!'
        except QuotaException as e:
            assert e.message == 'User has too many opened tasks!', 'Wrong exception message!'

    def test_change_priority(self):
        task = Task.create_task(self.get_user(), 'Task1', 5, timezone.now(),
                                [CrawlingType.objects.get(type=CrawlingType.TEXT)], 'onet.pl', max_links=400)
        assert 5 == task.priority
        task.change_priority(10)
        assert 10 == task.priority
        try:
            task.change_priority(15)
            assert False, 'Exception should be raised!'
        except QuotaException as e:
            assert e.message == 'Task priority exceeds user quota!', 'Wrong exception message!'
        assert 10 == task.priority

    def test_pause_and_resume(self):
        task = Task.create_task(self.get_user(), 'Task1', 5, timezone.now(),
                                [CrawlingType.objects.get(type=CrawlingType.TEXT)], 'onet.pl', max_links=400)
        assert task.active
        task.pause()
        assert not task.active
        task.resume()
        assert task.active

    def test_finish(self):
        task = Task.create_task(self.get_user(), 'Task1', 5, timezone.now(),
                                [CrawlingType.objects.get(type=CrawlingType.TEXT)], 'onet.pl', max_links=400)

        try:
            Task.create_task(self.get_user(), 'Task1', 5, timezone.now(),
                             [CrawlingType.objects.get(type=CrawlingType.TEXT)], 'onet.pl', max_links=400)
            assert False, 'Exception should be raised!'
        except QuotaException as e:
            assert e.message == 'User has too many opened tasks!', 'Wrong exception message!'
        task.stop()
        assert task.finished
        Task.create_task(self.get_user(), 'Task2', 5, timezone.now(), [CrawlingType.objects.get(type=CrawlingType.TEXT)],
                         'onet.pl', max_links=400)
