from oauth2_provider.models import Application
from models import User, QuotaException, Task, CrawlingType
from django.utils import timezone
from django.test.client import Client
import json
from django_pytest.conftest import pytest_funcarg__client, pytest_funcarg__django_client

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

        CrawlingType.objects.create(type=CrawlingType.TEXT)
        CrawlingType.objects.create(type=CrawlingType.LINKS)
        CrawlingType.objects.create(type=CrawlingType.PICTURES)

    def teardown(self):
        self.user.delete()
        CrawlingType.objects.all().delete()

    def test_successful_task_creation(self, client):
        Task.objects.create_task(self.get_user(), 'Task1', 3, timezone.now(),
                                [CrawlingType.objects.get(type=CrawlingType.TEXT)], 'onet.pl', max_links=400)
        assert self.get_user().task_set.count() == 1, 'Task was not properly saved!'

    def test_failed_task_creation(self, client):
        try:
            Task.objects.create_task(self.get_user(), 'Task1', 12, timezone.now(),
                             [CrawlingType.objects.get(type=CrawlingType.TEXT)], 'onet.pl', max_links=400)
            assert False, 'Exception should be raised!'
        except QuotaException as e:
            assert e.message.startswith('Task priority exceeds user quota!'), 'Wrong exception message!'

        try:
            Task.objects.create_task(self.get_user(), 'Task1', 5, timezone.now(),
                             [CrawlingType.objects.get(type=CrawlingType.TEXT)], 'onet.pl', max_links=1400)
            assert False, 'Exception should be raised!'
        except QuotaException as e:
            assert e.message.startswith('Task link limit exceeds user quota!'), 'Wrong exception message!'

    def test_change_priority(self, client):
        task = Task.objects.create_task(self.get_user(), 'Task1', 5, timezone.now(),
                                [CrawlingType.objects.get(type=CrawlingType.TEXT)], 'onet.pl', max_links=400)
        assert task.priority == 5
        task.change_priority(7)
        assert task.priority == 7
        try:
            task.change_priority(12)
            assert False, 'Exception should be raised!'
        except QuotaException as e:
            assert str(e).startswith('Task priority exceeds user quota!'), 'Wrong exception message!'
        assert task.priority == 7

        Task.objects.create_task(self.get_user(), 'Task2', 7, timezone.now(),
                         [CrawlingType.objects.get(type=CrawlingType.TEXT)], 'onet.pl', max_links=400)
        try:
            task.change_priority(9)
            assert False, 'Exception should be raised!'
        except QuotaException as e:
            assert str(e).startswith('User priority pool exceeded!'), 'Wrong exception message!' + str(e)
        assert task.priority == 7

    def test_pause_and_resume(self, client):
        task = Task.objects.create_task(self.get_user(), 'Task1', 5, timezone.now(),
                                [CrawlingType.objects.get(type=CrawlingType.TEXT)], 'onet.pl', max_links=400)
        assert task.active
        task.pause()
        assert not task.active
        task.resume()
        assert task.active

    def test_finish(self, client):
        task = Task.objects.create_task(self.get_user(), 'Task1', 5, timezone.now(),
                                [CrawlingType.objects.get(type=CrawlingType.TEXT)], 'onet.pl', max_links=400)

        try:
            Task.objects.create_task(self.get_user(), 'Task2', 5, timezone.now(),
                             [CrawlingType.objects.get(type=CrawlingType.TEXT)], 'onet.pl', max_links=400)
            Task.objects.create_task(self.get_user(), 'Task3', 5, timezone.now(),
                                     [CrawlingType.objects.get(type=CrawlingType.TEXT)], 'onet.pl', max_links=400)
            assert False, 'Exception should be raised!'
        except QuotaException as e:
            assert str(e).startswith('User has too many opened tasks!'), 'Wrong exception message!'
        task.stop()
        assert task.finished
        Task.objects.create_task(self.get_user(), 'Task3', 5, timezone.now(), [CrawlingType.objects.get(type=CrawlingType.TEXT)],
                         'onet.pl', max_links=400)


class TestREST:
    def setup(self):
        self.user = User.objects.create_user(username='test_user', password='test_pwd', email='test@gmail.pl')
        self.user.is_active = True
        self.user.save()
        self.user.quota.max_tasks = 2
        self.user.quota.max_links = 1000
        self.user.quota.max_priority = 10
        self.user.quota.link_pool = 1500
        self.user.quota.priority_pool = 15
        self.user.quota.save()

        CrawlingType.objects.create(type=CrawlingType.TEXT)
        CrawlingType.objects.create(type=CrawlingType.LINKS)
        CrawlingType.objects.create(type=CrawlingType.PICTURES)

        self.user2 = User.objects.create_user(username='test_user2', password='test_pwd2', email='test@gmail.pl')
        self.user2_task = Task.objects.create_task(self.user2, 'Task test_user2', 5, timezone.now(),
                                                   [CrawlingType.objects.get(type=CrawlingType.TEXT)], 'onet.pl',
                                                   max_links=400)

        self.client = Client()
        app = Application.objects.create(user=self.user, client_type=Application.CLIENT_CONFIDENTIAL,
                                         authorization_grant_type=Application.GRANT_PASSWORD)
        app.save()

        resp = self.client.post('/o/token/', {'grant_type': 'password', 'username': 'test_user',
                                'password': 'test_pwd', 'client_id': app.client_id,
                                'client_secret': app.client_secret})
        resp_json = json.loads(resp.content)
        self.token = resp_json['access_token']
        self.token_type = resp_json['token_type']

    def teardown(self):
        self.user.delete()
        CrawlingType.objects.all().delete()

    def test_add_task(self, client):
        resp = self.client.post('/api/task/add/', {'name': 'Task1', 'priority': 11, 'expire': timezone.now(),
                                'types': [1], 'whitelist': 'onet', 'blacklist': 'wp', 'max_links': 100},
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 412
        assert self.user.task_set.count() == 0

        resp = self.client.post('/api/task/add/', {'name': 'Task1', 'priority': 2, 'expire': timezone.now(),
                                'types': [1], 'whitelist': 'onet', 'blacklist': 'wp', 'max_links': -100},
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 412
        assert self.user.task_set.count() == 0

        resp = self.client.post('/api/task/add/', {'name': 'Task1', 'priority': 2, 'expire': timezone.now(),
                                'types': [1], 'whitelist': 'onet', 'blacklist': 'wp'},
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 400
        assert self.user.task_set.count() == 0

        resp = self.client.post('/api/task/add/', {'name': 'Task1', 'priority': 2, 'expire': timezone.now(),
                                'types': [1], 'whitelist': 'onet', 'blacklist': 'wp', 'max_links': 100},
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 201
        assert json.loads(resp.content)['id'] > 0
        assert self.user.task_set.count() == 1

    def test_pause_resume_task(self, client):
        resp = self.client.post('/api/task/add/', {'name': 'Task1', 'priority': 10, 'expire': timezone.now(),
                                'types': [1], 'whitelist': 'onet', 'blacklist': 'wp', 'max_links': 100},
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        task_id = json.loads(resp.content)['id']
        assert resp.status_code == 201
        assert Task.objects.filter(id=task_id).first().active, resp.content

        resp = self.client.post('/api/task/pause/' + str(task_id) + '/',
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 200
        assert not Task.objects.filter(id=task_id).first().active, resp.content

        resp = self.client.post('/api/task/add/', {'name': 'Task1', 'priority': 8, 'expire': timezone.now(),
                                'types': [1], 'whitelist': 'onet', 'blacklist': 'wp', 'max_links': 100},
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        task2_id = json.loads(resp.content)['id']
        assert resp.status_code == 201

        resp = self.client.post('/api/task/resume/' + str(task_id) + '/',
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 412
        assert not Task.objects.filter(id=task_id).first().active, resp.content

        resp = self.client.post('/api/task/delete/' + str(task2_id) + '/',
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 200

        resp = self.client.post('/api/task/resume/' + str(task_id) + '/',
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 200
        assert Task.objects.filter(id=task_id).first().active, resp.content

        resp = self.client.post('/api/task/pause/' + str(self.user2_task.id) + '/',
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 403
        assert Task.objects.filter(id=self.user2_task.id).first().active, resp.content

        resp = self.client.post('/api/task/resume/' + str(self.user2_task.id) + '/',
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 403
        assert Task.objects.filter(id=self.user2_task.id).first().active, resp.content

        resp = self.client.post('/api/task/pause/500/',
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 404

        resp = self.client.post('/api/task/resume/500/',
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 404

    def test_stop_task(self, client):
        resp = self.client.post('/api/task/add/', {'name': 'Task1', 'priority': 2, 'expire': timezone.now(),
                                                   'types': [1], 'whitelist': 'onet', 'blacklist': 'wp', 'max_links': 100},
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 201
        task_id = json.loads(resp.content)['id']
        assert Task.objects.filter(id=task_id).first().active
        assert not Task.objects.filter(id=task_id).first().finished

        resp = self.client.post('/api/task/delete/' + str(task_id) + '/',
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 200
        assert not Task.objects.filter(id=task_id).first().active
        assert Task.objects.filter(id=task_id).first().finished

        resp = self.client.post('/api/task/resume/' + str(task_id) + '/',
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 200
        assert not Task.objects.filter(id=task_id).first().active

        resp = self.client.post('/api/task/delete/' + str(self.user2_task.id) + '/',
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 403
        assert not Task.objects.filter(id=self.user2_task.id).first().finished

        resp = self.client.post('/api/task/delete/500/',
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 404

