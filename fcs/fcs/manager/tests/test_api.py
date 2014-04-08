import json
from django.core.urlresolvers import reverse
from oauth2_provider.models import Application
from django.test.client import Client
from django.utils import timezone
from fcs.manager.models import User, Task
from django_pytest.conftest import pytest_funcarg__client, pytest_funcarg__django_client
#Do not remove previous line


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
        
        self.user2 = User.objects.create_user(username='test_user2', password='test_pwd2', email='test@gmail.pl')
        self.user2_task = Task.objects.create_task(self.user2, 'Task test_user2', 5, timezone.now(), 'http://onet.pl',
                                                   max_links=400)

        self.client = Client()
        app = Application.objects.create(user=self.user, client_type=Application.CLIENT_CONFIDENTIAL,
                                         authorization_grant_type=Application.GRANT_PASSWORD)
        app.save()

        resp = self.client.post(reverse('oauth2_provider:token'), {'grant_type': 'password', 'username': 'test_user',
                                'password': 'test_pwd', 'client_id': app.client_id,
                                'client_secret': app.client_secret})
        resp_json = json.loads(resp.content)
        self.token = resp_json['access_token']
        self.token_type = resp_json['token_type']

    def teardown(self):
        self.user.delete()
        self.user2.delete()

    def test_add_task_success(self, client):
        resp = self.client.post(reverse('api:add_task'), {'name': 'Task1', 'priority': 2, 'expire': timezone.now(),
                                'mime_type': 'text/html', 'whitelist': 'onet', 'blacklist': 'wp', 'max_links': 100,
                                'start_links': 'http://onet.pl'},
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 201
        assert json.loads(resp.content)['id'] > 0
        assert self.user.task_set.count() == 1

    def test_add_task_failed_priority_quota(self, client):
        resp = self.client.post(reverse('api:add_task'), {'name': 'Task1', 'priority': 11, 'expire': timezone.now(),
                                                          'mime_type': 'text/html', 'whitelist': 'onet', 'blacklist': 'wp',
                                                          'max_links': 100, 'start_links': 'http://onet.pl'},
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 412
        assert self.user.task_set.count() == 0

    def test_add_task_failed_incorrect_links(self, client):
        resp = self.client.post(reverse('api:add_task'), {'name': 'Task1', 'priority': 2, 'expire': timezone.now(),
                                                          'mime_type': 'text/html', 'whitelist': 'onet', 'blacklist': 'wp',
                                                          'max_links': -100, 'start_links': 'http://onet.pl'},
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 412
        assert self.user.task_set.count() == 0

    def test_add_task_failed_incorrect_dataset(self, client):
        resp = self.client.post(reverse('api:add_task'), {'name': 'Task1', 'priority': 2, 'expire': timezone.now(),
                                                          'mime_type': 'text/html', 'whitelist': 'onet', 'blacklist': 'wp',
                                                          'start_links': 'http://onet.pl'},
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 400
        assert self.user.task_set.count() == 0

    def test_pause_task_success(self, client):
        task = Task.objects.create_task(self.user, 'Task1', 10, timezone.now(), 'http://onet.pl', max_links=400)
        assert Task.objects.filter(id=task.id).first().active

        resp = self.client.post(reverse('api:pause_task', kwargs={'task_id': task.id}),
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 200
        assert not Task.objects.filter(id=task.id).first().active, resp.content

    def test_resume_task_success(self, client):
        task = Task.objects.create_task(self.user, 'Task1', 10, timezone.now(), 'http://onet.pl', max_links=400)
        task.pause()
        assert not Task.objects.filter(id=task.id).first().active

        resp = self.client.post(reverse('api:resume_task', kwargs={'task_id': task.id}),
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 200
        assert Task.objects.filter(id=task.id).first().active, resp.content

    def test_resume_task_failed_priority_pool(self, client):
        task = Task.objects.create_task(self.user, 'Task1', 10, timezone.now(), 'http://onet.pl', max_links=400)
        task.pause()
        Task.objects.create_task(self.user, 'Task2', 7, timezone.now(), 'http://onet.pl', max_links=400)
        assert not Task.objects.filter(id=task.id).first().active

        resp = self.client.post(reverse('api:resume_task', kwargs={'task_id': task.id}),
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 412
        assert not Task.objects.filter(id=task.id).first().active, resp.content

    def test_pause_task_failed_authorization(self, client):
        resp = self.client.post(reverse('api:pause_task', kwargs={'task_id': self.user2_task.id}),
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 403
        assert Task.objects.filter(id=self.user2_task.id).first().active, resp.content

    def test_resume_task_failed_authorization(self, client):
        resp = self.client.post(reverse('api:resume_task', kwargs={'task_id': self.user2_task.id}),
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 403
        assert Task.objects.filter(id=self.user2_task.id).first().active, resp.content

    def test_pause_task_failed_incorrect_id(self, client):
        resp = self.client.post(reverse('api:pause_task', kwargs={'task_id': '500'}),
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 404

    def test_resume_task_failed_incorrect_id(self, client):
        resp = self.client.post(reverse('api:resume_task', kwargs={'task_id': '500'}),
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 404

    def test_resume_task_failed_finished(self, client):
        task = Task.objects.create_task(self.user, 'Task1', 2, timezone.now(), 'http://onet.pl', max_links=400)
        task.stop()
        assert not Task.objects.filter(id=task.id).first().active
        assert Task.objects.filter(id=task.id).first().finished

        resp = self.client.post(reverse('api:resume_task', kwargs={'task_id': task.id}),
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 200
        assert not Task.objects.filter(id=task.id).first().active

    def test_stop_task_success(self, client):
        task = Task.objects.create_task(self.user, 'Task1', 2, timezone.now(), 'http://onet.pl', max_links=400)
        assert Task.objects.filter(id=task.id).first().active
        assert not Task.objects.filter(id=task.id).first().finished

        resp = self.client.post(reverse('api:delete_task', kwargs={'task_id': task.id}),
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 200
        assert not Task.objects.filter(id=task.id).first().active
        assert Task.objects.filter(id=task.id).first().finished

    def test_stop_task_failed_authorization(self, client):
        resp = self.client.post(reverse('api:delete_task', kwargs={'task_id': self.user2_task.id}),
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 403
        assert not Task.objects.filter(id=self.user2_task.id).first().finished

    def test_stop_task_failed_incorrect_id(self, client):
        resp = self.client.post(reverse('api:delete_task', kwargs={'task_id': '500'}),
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 404
