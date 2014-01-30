from django.forms.forms import BoundField
from django.forms.widgets import PasswordInput
from oauth2_provider.models import Application
from models import User, QuotaException, Task, CrawlingType
from django.utils import timezone
from django.test.client import Client
from django.core.urlresolvers import reverse
import json
from django import forms
from templatetags.custom_tags import is_class, alert_tag
from accounts.forms import LoginForm
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

        resp = self.client.post(reverse('oauth2_provider:token'), {'grant_type': 'password', 'username': 'test_user',
                                'password': 'test_pwd', 'client_id': app.client_id,
                                'client_secret': app.client_secret})
        resp_json = json.loads(resp.content)
        self.token = resp_json['access_token']
        self.token_type = resp_json['token_type']

    def teardown(self):
        self.user.delete()
        self.user2.delete()
        CrawlingType.objects.all().delete()

    def test_add_task(self, client):
        resp = self.client.post(reverse('api:add_task'), {'name': 'Task1', 'priority': 11, 'expire': timezone.now(),
                                'types': [1], 'whitelist': 'onet', 'blacklist': 'wp', 'max_links': 100},
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 412
        assert self.user.task_set.count() == 0

        resp = self.client.post(reverse('api:add_task'), {'name': 'Task1', 'priority': 2, 'expire': timezone.now(),
                                'types': [1], 'whitelist': 'onet', 'blacklist': 'wp', 'max_links': -100},
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 412
        assert self.user.task_set.count() == 0

        resp = self.client.post(reverse('api:add_task'), {'name': 'Task1', 'priority': 2, 'expire': timezone.now(),
                                'types': [1], 'whitelist': 'onet', 'blacklist': 'wp'},
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 400
        assert self.user.task_set.count() == 0

        resp = self.client.post(reverse('api:add_task'), {'name': 'Task1', 'priority': 2, 'expire': timezone.now(),
                                'types': [1], 'whitelist': 'onet', 'blacklist': 'wp', 'max_links': 100},
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 201
        assert json.loads(resp.content)['id'] > 0
        assert self.user.task_set.count() == 1

    def test_pause_resume_task(self, client):
        resp = self.client.post(reverse('api:add_task'), {'name': 'Task1', 'priority': 10, 'expire': timezone.now(),
                                'types': [1], 'whitelist': 'onet', 'blacklist': 'wp', 'max_links': 100},
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        task_id = json.loads(resp.content)['id']
        assert resp.status_code == 201
        assert Task.objects.filter(id=task_id).first().active, resp.content

        resp = self.client.post(reverse('api:pause_task', kwargs={'task_id': task_id}),
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 200
        assert not Task.objects.filter(id=task_id).first().active, resp.content

        resp = self.client.post(reverse('api:add_task'), {'name': 'Task1', 'priority': 8, 'expire': timezone.now(),
                                'types': [1], 'whitelist': 'onet', 'blacklist': 'wp', 'max_links': 100},
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        task2_id = json.loads(resp.content)['id']
        assert resp.status_code == 201

        resp = self.client.post(reverse('api:resume_task', kwargs={'task_id': task_id}),
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 412
        assert not Task.objects.filter(id=task_id).first().active, resp.content

        resp = self.client.post(reverse('api:delete_task', kwargs={'task_id': task2_id}),
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 200

        resp = self.client.post(reverse('api:resume_task', kwargs={'task_id': task_id}),
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 200
        assert Task.objects.filter(id=task_id).first().active, resp.content

        resp = self.client.post(reverse('api:pause_task', kwargs={'task_id': self.user2_task.id}),
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 403
        assert Task.objects.filter(id=self.user2_task.id).first().active, resp.content

        resp = self.client.post(reverse('api:resume_task', kwargs={'task_id': self.user2_task.id}),
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 403
        assert Task.objects.filter(id=self.user2_task.id).first().active, resp.content

        resp = self.client.post(reverse('api:pause_task', kwargs={'task_id': '500'}),
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 404

        resp = self.client.post(reverse('api:resume_task', kwargs={'task_id': '500'}),
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 404

    def test_stop_task(self, client):
        resp = self.client.post(reverse('api:add_task'), {'name': 'Task1', 'priority': 2, 'expire': timezone.now(),
                                'types': [1], 'whitelist': 'onet', 'blacklist': 'wp', 'max_links': 100},
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 201
        task_id = json.loads(resp.content)['id']
        assert Task.objects.filter(id=task_id).first().active
        assert not Task.objects.filter(id=task_id).first().finished

        resp = self.client.post(reverse('api:delete_task', kwargs={'task_id': task_id}),
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 200
        assert not Task.objects.filter(id=task_id).first().active
        assert Task.objects.filter(id=task_id).first().finished

        resp = self.client.post(reverse('api:resume_task', kwargs={'task_id': task_id}),
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 200
        assert not Task.objects.filter(id=task_id).first().active

        resp = self.client.post(reverse('api:delete_task', kwargs={'task_id': self.user2_task.id}),
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 403
        assert not Task.objects.filter(id=self.user2_task.id).first().finished

        resp = self.client.post(reverse('api:delete_task', kwargs={'task_id': '500'}),
                                AUTHORIZATION=self.token_type + ' ' + self.token)
        assert resp.status_code == 404


class TestTemplateTags:
    def test_is_class(self):
        form = LoginForm()
        field = BoundField(form, forms.CharField(), 'name')
        assert is_class(field, 'TextInput')
        field = BoundField(form, forms.CharField(widget=PasswordInput()), 'name')
        assert is_class(field, 'PasswordInput')

    def test_alert_tag(self):
        assert alert_tag('debug') == ''
        assert alert_tag('info') == 'alert-info'
        assert alert_tag('success') == 'alert-success'
        assert alert_tag('warning') == 'alert-warning'
        assert alert_tag('error') == 'alert-danger'
        assert alert_tag('bad_tag') == 'alert-info'


class TestViews:
    def setup(self):
        self.user = User.objects.create_user(username='test_user', password='test_pwd', email='test@gmail.pl')
        self.user.is_active = True
        self.user.save()

        self.client = Client()
        self.client.login(username='test_user', password='test_pwd')

    def teardown(self):
        self.user.delete()

    def test_index(self, client):
        resp = self.client.get(reverse('index'))
        assert resp.status_code == 200

    def test_login(self, client):
        self.client.logout()
        resp = self.client.get(reverse('login'), follow=True)
        assert resp.status_code == 200

        resp = self.client.post(reverse('login'), {'password': 'test_pwd'}, follow=True)
        assert not resp.context['user'].id

        self.user.is_active = False
        self.user.save()
        resp = self.client.post(reverse('login'), {'username': 'test_user', 'password': 'test_pwd'}, follow=True)
        assert 'Account is not activated. Check your email.' in self.messages(resp)
        assert not resp.context['user'].id
        self.user.is_active = True
        self.user.save()

        resp = self.client.post(reverse('login'), {'username': 'bad_user', 'password': 'test_pwd'}, follow=True)
        assert 'Authentication failed. Incorrect username or password.' in self.messages(resp)
        assert not resp.context['user'].id

        resp = self.client.post(reverse('login'), {'username': 'test_user', 'password': 'test_pwd'}, follow=True)
        assert 'Login successful.' in self.messages(resp)
        assert resp.context['user'].id

        resp = self.client.get(reverse('login'), follow=True)
        assert 'You are already logged in.' in self.messages(resp)
        assert resp.context['user'].id

    def test_logout(self, client):
        resp = self.client.get(reverse('index'), follow=True)
        assert resp.context['user'].id

        resp = self.client.get(reverse('logout'), follow=True)
        assert 'Logout successful.' in self.messages(resp)
        assert not resp.context['user'].id

    def test_change_password(self, client):
        resp = self.client.get(reverse('change_password'), follow=True)
        assert resp.status_code == 200
        assert resp.context['user'].id

        resp = self.client.post(reverse('change_password'), {'old_password': 'bad_pwd', 'password': 't',
                                'password_again': 't'}, follow=True)
        assert 'Old password is incorrect.' in self.messages(resp)
        assert resp.context['user'].id

        resp = self.client.post(reverse('change_password'), {'old_password': 'test_pwd', 'password': 't',
                                'password_again': 't'}, follow=True)
        assert 'Password changed successfully. Please log-in again.' in self.messages(resp)
        assert not resp.context['user'].id

        assert not self.client.login(username='test_user', password='test_pwd')
        assert self.client.login(username='test_user', password='t')

    def test_list_tasks(self, client):
        resp = self.client.get(reverse('list_tasks'), follow=True)
        assert resp.status_code == 200

    def test_add_task(self, client):
        resp = self.client.get(reverse('add_task'), follow=True)
        assert resp.status_code == 200

        assert self.user.task_set.count() == 0
        resp = self.client.post(reverse('add_task'), {'name': 'Task1', 'priority': '20', 'whitelist': 'onet',
                                'blacklist': 'wp', 'max_links': '100', 'expire': timezone.now(), 'type': ['0']},
                                follow=True)
        assert self.user.task_set.count() == 0, resp
        resp = self.client.post(reverse('add_task'), {'name': 'Task1', 'priority': '10', 'whitelist': 'onet',
                                'blacklist': 'wp', 'max_links': '100', 'expire': timezone.datetime.now(), 'type': ['0']},
                                follow=True)
        assert self.user.task_set.count() == 1, resp
        assert 'New task created.' in self.messages(resp)

    def test_show_task(self, client):
        resp = self.client.get(reverse('show_task', kwargs={'task_id': '1'}), follow=True)
        assert resp.status_code == 404

        task = Task.objects.create_task(self.user, 'task', 10, timezone.now(),
                                 [], 'onet.pl',
                                 max_links=400)
        assert Task.objects.filter(id=1).first().priority == 10

        resp = self.client.get(reverse('show_task', kwargs={'task_id': '1'}), follow=True)
        assert resp.status_code == 200

        resp = self.client.post(reverse('show_task', kwargs={'task_id': '1'}),
                                {'priority': '5', 'whitelist': 'onet', 'blacklist': 'wp',
                                'max_links': '10', 'expire_date': timezone.datetime.now()}, follow=True)
        assert Task.objects.filter(id=1).first().priority == 5, resp
        assert 'Task %s updated.' % task.name in self.messages(resp)

    def test_api_keys(self, client):
        resp = self.client.get(reverse('api_keys'), follow=True)
        assert resp.status_code == 200
        assert Application.objects.all().count() == 0

        resp = self.client.post(reverse('api_keys'), follow=True)
        assert resp.status_code == 200
        assert Application.objects.all().count() == 1

    def test_pause_task(self, client):
        task = Task.objects.create_task(self.user, 'task', 5, timezone.now(),
                                        [], 'onet.pl', max_links=400)
        assert Task.objects.get(id=task.id).active

        resp = self.client.get(reverse('pause_task', kwargs={'task_id': '2'}), follow=True)
        assert resp.status_code == 404

        resp = self.client.get(reverse('pause_task', kwargs={'task_id': '1'}), follow=True)
        assert not Task.objects.get(id=task.id).active
        assert 'Task %s paused.' % task.name in self.messages(resp)

        resp = self.client.get(reverse('pause_task', kwargs={'task_id': '1'}), follow=True)
        assert not Task.objects.get(id=task.id).active
        assert 'Task already paused!' in self.messages(resp)

        task.stop()
        resp = self.client.get(reverse('pause_task', kwargs={'task_id': '1'}), follow=True)
        assert not Task.objects.get(id=task.id).active
        assert 'Task already finished!' in self.messages(resp)

    def test_resume_task(self, client):
        task = Task.objects.create_task(self.user, 'task', 5, timezone.now(),
                                        [], 'onet.pl', max_links=400)
        assert Task.objects.get(id=task.id).active

        resp = self.client.get(reverse('resume_task', kwargs={'task_id': '2'}), follow=True)
        assert resp.status_code == 404

        resp = self.client.get(reverse('resume_task', kwargs={'task_id': '1'}), follow=True)
        assert Task.objects.get(id=task.id).active
        assert 'Task already in progress!' in self.messages(resp)

        task.pause()
        resp = self.client.get(reverse('resume_task', kwargs={'task_id': '1'}), follow=True)
        assert Task.objects.get(id=task.id).active
        assert 'Task %s resumed.' % task.name in self.messages(resp)

        task.stop()
        resp = self.client.get(reverse('resume_task', kwargs={'task_id': '1'}), follow=True)
        assert not Task.objects.get(id=task.id).active
        assert 'Task already finished!' in self.messages(resp)

    def test_stop_task(self, client):
        task = Task.objects.create_task(self.user, 'task', 5, timezone.now(),
                                        [], 'onet.pl', max_links=400)
        assert not Task.objects.get(id=task.id).finished

        resp = self.client.get(reverse('stop_task', kwargs={'task_id': '2'}), follow=True)
        assert resp.status_code == 404

        resp = self.client.get(reverse('stop_task', kwargs={'task_id': '1'}), follow=True)
        assert Task.objects.get(id=task.id).finished
        assert 'Task %s stopped.' % task.name in self.messages(resp)

        resp = self.client.get(reverse('stop_task', kwargs={'task_id': '1'}), follow=True)
        assert Task.objects.get(id=task.id).finished
        assert 'Task already finished!' in self.messages(resp)

    def test_get_data(self, client):
        task = Task.objects.create_task(self.user, 'task', 5, timezone.now(),
                                        [], 'onet.pl', max_links=400)

        resp = self.client.get(reverse('get_data', kwargs={'task_id': '2'}), follow=True)
        assert resp.status_code == 404

        resp = self.client.get(reverse('get_data', kwargs={'task_id': '1'}), follow=True)
        assert resp.status_code == 200
        old_date = Task.objects.get(id=task.id).last_data_download
        resp = self.client.get(reverse('get_data', kwargs={'task_id': '1'}), follow=True)
        assert resp.status_code == 200
        new_date = Task.objects.get(id=task.id).last_data_download
        assert new_date > old_date

    def test_edit_user_data(self, client):
        resp = self.client.get(reverse('edit_user_data'), follow=True)
        assert resp.status_code == 200

        resp = self.client.post(reverse('edit_user_data'), {'last_name': 'last', 'first_name': 'first',
                                                            'email': 'mail@mail.pl'}, follow=True)
        assert resp.status_code == 200
        assert 'Your data updated!' in self.messages(resp)

    def test_show_quota(self, client):
        resp = self.client.get(reverse('show_quota'), follow=True)
        assert resp.status_code == 200

    def messages(self, resp):
        return [msg.message for msg in resp.context['messages'].__iter__()]