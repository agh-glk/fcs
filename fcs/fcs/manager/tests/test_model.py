from django.core.exceptions import ValidationError
from fcs.manager.models import User, QuotaException, Task
from django.utils import timezone
from django_pytest.conftest import pytest_funcarg__client, pytest_funcarg__django_client
#Do not remove previous line


class TestTask:
    def get_user(self):
        if self.user is None:
            self.user = User.objects.get(username='test_user')
        return self.user

    def setup(self):
        self.user = User.objects.create_user(username='test_user', password='test_pwd', email='test@gmail.pl')
        self.get_user().quota.max_tasks = 2
        self.get_user().quota.max_links = 1000
        self.get_user().quota.max_priority = 10
        self.get_user().quota.link_pool = 1500
        self.get_user().quota.priority_pool = 15
        self.get_user().quota.save()

    def teardown(self):
        self.user.delete()

    def test_successful_task_creation(self, client):
        task = Task.objects.create_task(self.get_user(), 'Task1', 3, timezone.now(), 'http://onet.pl\nhttps://wp.pl',
                                        max_links=400, mime_type='')
        assert self.get_user().task_set.count() == 1, 'Task was not properly saved!'
        assert task.mime_type == 'text/html', 'Wrong default MIME type value'

    def test_failed_task_creation_wrong_links_protocol(self, client):
        try:
            Task.objects.create_task(self.get_user(), 'Task1', 3, timezone.now(), 'http://onet.pl\nhtt://wp.pl',
                                     max_links=400)
            assert False, 'Exception should be raised!'
        except ValidationError as e:
            assert e.message.startswith('Invalid protocol in start links! Only http and https are valid.'), 'Wrong exception message!' + str(e)

    def test_failed_task_creation_priority_quota(self, client):
        try:
            Task.objects.create_task(self.get_user(), 'Task1', 12, timezone.now(), 'http://onet.pl', max_links=400)
            assert False, 'Exception should be raised!'
        except QuotaException as e:
            assert e.message.startswith('Task priority exceeds user quota!'), 'Wrong exception message!'

    def test_failed_task_creation_link_quota(self, client):
        try:
            Task.objects.create_task(self.get_user(), 'Task1', 5, timezone.now(), 'http://onet.pl', max_links=1400)
            assert False, 'Exception should be raised!'
        except QuotaException as e:
            assert e.message.startswith('Task link limit exceeds user quota!'), 'Wrong exception message!'

    def test_change_priority_success(self, client):
        task = Task.objects.create_task(self.get_user(), 'Task1', 5, timezone.now(), 'http://onet.pl', max_links=400)
        assert task.priority == 5
        task.change_priority(7)

    def test_change_priority_failed_priority_quota(self, client):
        task = Task.objects.create_task(self.get_user(), 'Task1', 5, timezone.now(), 'http://onet.pl', max_links=400)
        assert task.priority == 5
        try:
            task.change_priority(12)
            assert False, 'Exception should be raised!'
        except QuotaException as e:
            assert str(e).startswith('Task priority exceeds user quota!'), 'Wrong exception message!'
        assert task.priority == 5

    def test_change_priority_failed_priority_pool_quota(self, client):
        task = Task.objects.create_task(self.get_user(), 'Task1', 7, timezone.now(), 'http://onet.pl', max_links=400)
        Task.objects.create_task(self.get_user(), 'Task2', 7, timezone.now(), 'http://onet.pl', max_links=400)
        try:
            task.change_priority(9)
            assert False, 'Exception should be raised!'
        except QuotaException as e:
            assert str(e).startswith('User priority pool exceeded!'), 'Wrong exception message!' + str(e)
        assert task.priority == 7

    def test_pause(self, client):
        task = Task.objects.create_task(self.get_user(), 'Task1', 5, timezone.now(), 'http://onet.pl', max_links=400)
        assert task.active
        task.pause()
        assert not task.active

    def test_resume(self, client):
        task = Task.objects.create_task(self.get_user(), 'Task1', 5, timezone.now(), 'http://onet.pl', max_links=400)
        task.active = False
        task.save()
        assert not task.active
        task.resume()
        assert task.active

    def test_finish(self, client):
        task = Task.objects.create_task(self.get_user(), 'Task1', 5, timezone.now(), 'http://onet.pl', max_links=400)
        try:
            Task.objects.create_task(self.get_user(), 'Task2', 5, timezone.now(), 'http://onet.pl', max_links=400)
            Task.objects.create_task(self.get_user(), 'Task3', 5, timezone.now(), 'http://onet.pl', max_links=400)
            assert False, 'Exception should be raised!'
        except QuotaException as e:
            assert str(e).startswith('User has too many opened tasks!'), 'Wrong exception message!'
        task.stop()
        assert task.finished
        Task.objects.create_task(self.get_user(), 'Task3', 5, timezone.now(), 'http://onet.pl', max_links=400)
