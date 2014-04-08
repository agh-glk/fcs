from fcs.manager.models import User, Task, create_api_keys
from oauth2_provider.models import Application
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.utils import timezone
from django_pytest.conftest import pytest_funcarg__client, pytest_funcarg__django_client
#Do not remove previous line


class TestViews:
    def setup(self):
        self.user = User.objects.create_user(username='test_user', password='test_pwd', email='test@gmail.pl')
        self.user.is_active = True
        create_api_keys(None, user=self.user)
        self.user.save()

        self.client = Client()
        self.client.login(username='test_user', password='test_pwd')

    def teardown(self):
        self.user.delete()

    def test_index(self, client):
        resp = self.client.get(reverse('index'))
        assert resp.status_code == 200

    def test_list_tasks(self, client):
        resp = self.client.get(reverse('list_tasks'), follow=True)
        assert resp.status_code == 200

    def test_add_task_get(self, client):
        resp = self.client.get(reverse('add_task'), follow=True)
        assert resp.status_code == 200

    def test_add_task_post_failed(self, client):
        assert self.user.task_set.count() == 0
        resp = self.client.post(reverse('add_task'), {'name': 'Task1', 'priority': '20', 'whitelist': 'onet',
                                'blacklist': 'wp', 'max_links': '100', 'expire': timezone.now(), 
                                'mime_type': 'text/html', 'start_links': 'http://onet.pl'},
                                follow=True)
        assert self.user.task_set.count() == 0, resp

    def test_add_task_post_success(self, client):
        assert self.user.task_set.count() == 0
        resp = self.client.post(reverse('add_task'), {'name': 'Task1', 'priority': '10', 'whitelist': 'onet',
                                'blacklist': 'wp', 'max_links': '100', 'expire': timezone.datetime.now(), 
                                'mime_type': 'text/html', 'start_links': 'http://onet.pl'},
                                follow=True)
        assert self.user.task_set.count() == 1, resp
        assert 'New task created.' in self.messages(resp)

    def test_show_task_get_failed_incorrect_id(self, client):
        resp = self.client.get(reverse('show_task', kwargs={'task_id': '500'}), follow=True)
        assert resp.status_code == 404

    def test_show_task_get_success(self, client):
        task = Task.objects.create_task(self.user, 'task', 10, timezone.now(), 'http://onet.pl', max_links=400)

        resp = self.client.get(reverse('show_task', kwargs={'task_id': task.id}), follow=True)
        assert resp.status_code == 200

    def test_show_task_post_success(self, client):
        task = Task.objects.create_task(self.user, 'task', 10, timezone.now(), 'http://onet.pl', max_links=400)
        assert Task.objects.filter(id=task.id).first().priority == 10

        resp = self.client.post(reverse('show_task', kwargs={'task_id': task.id}),
                                {'priority': '5', 'whitelist': 'onet', 'blacklist': 'wp',
                                'max_links': '10', 'expire_date': timezone.datetime.now(),
                                'mime_type': 'text/html', 'start_links': 'http://onet.pl'}, follow=True)
        assert Task.objects.filter(id=task.id).first().priority == 5, resp
        assert 'Task %s updated.' % task.name in self.messages(resp)

    def test_api_keys(self, client):
        resp = self.client.get(reverse('api_keys'), follow=True)
        assert resp.status_code == 200
        assert Application.objects.all().count() == 1

    def test_pause_task_success(self, client):
        task = Task.objects.create_task(self.user, 'task', 5, timezone.now(),
                                        'http://onet.pl', max_links=400)
        assert Task.objects.get(id=task.id).active

        resp = self.client.get(reverse('pause_task', kwargs={'task_id': task.id}), follow=True)
        assert not Task.objects.get(id=task.id).active
        assert 'Task %s paused.' % task.name in self.messages(resp)

    def test_pause_task_failed_incorrect_id(self, client):
        resp = self.client.get(reverse('pause_task', kwargs={'task_id': '500'}), follow=True)
        assert resp.status_code == 404

    def test_pause_task_failed_already_paused(self, client):
        task = Task.objects.create_task(self.user, 'task', 5, timezone.now(),
                                        'http://onet.pl', max_links=400)
        task.pause()
        assert not Task.objects.get(id=task.id).active

        resp = self.client.get(reverse('pause_task', kwargs={'task_id': task.id}), follow=True)
        assert not Task.objects.get(id=task.id).active
        assert 'Task already paused!' in self.messages(resp)

    def test_pause_task_failed_finished(self, client):
        task = Task.objects.create_task(self.user, 'task', 5, timezone.now(),
                                        'http://onet.pl', max_links=400)
        task.stop()

        resp = self.client.get(reverse('pause_task', kwargs={'task_id': task.id}), follow=True)
        assert not Task.objects.get(id=task.id).active
        assert 'Task already finished!' in self.messages(resp)

    def test_resume_task_success(self, client):
        task = Task.objects.create_task(self.user, 'task', 5, timezone.now(),
                                        'http://onet.pl', max_links=400)
        task.pause()
        assert not Task.objects.get(id=task.id).active

        resp = self.client.get(reverse('resume_task', kwargs={'task_id': task.id}), follow=True)
        assert Task.objects.get(id=task.id).active
        assert 'Task %s resumed.' % task.name in self.messages(resp)

    def test_resume_task_failed_incorrect_id(self, client):
        resp = self.client.get(reverse('resume_task', kwargs={'task_id': '500'}), follow=True)
        assert resp.status_code == 404

    def test_resume_task_failed_already_running(self, client):
        task = Task.objects.create_task(self.user, 'task', 5, timezone.now(),
                                        'http://onet.pl', max_links=400)
        assert Task.objects.get(id=task.id).active

        resp = self.client.get(reverse('resume_task', kwargs={'task_id': task.id}), follow=True)
        assert Task.objects.get(id=task.id).active
        assert 'Task already in progress!' in self.messages(resp)

    def test_resume_task_failed_finished(self, client):
        task = Task.objects.create_task(self.user, 'task', 5, timezone.now(),
                                        'http://onet.pl', max_links=400)
        task.stop()
        assert not Task.objects.get(id=task.id).active
        assert Task.objects.get(id=task.id).finished

        resp = self.client.get(reverse('resume_task', kwargs={'task_id': task.id}), follow=True)
        assert not Task.objects.get(id=task.id).active
        assert 'Task already finished!' in self.messages(resp)

    def test_stop_task_success(self, client):
        task = Task.objects.create_task(self.user, 'task', 5, timezone.now(),
                                        'http://onet.pl', max_links=400)
        assert not Task.objects.get(id=task.id).finished

        resp = self.client.get(reverse('stop_task', kwargs={'task_id': task.id}), follow=True)
        assert Task.objects.get(id=task.id).finished
        assert 'Task %s stopped.' % task.name in self.messages(resp)

    def test_stop_task_failed_incorrect_id(self, client):
        resp = self.client.get(reverse('stop_task', kwargs={'task_id': '500'}), follow=True)
        assert resp.status_code == 404

    def test_stop_task_failed_already_finished(self, client):
        task = Task.objects.create_task(self.user, 'task', 5, timezone.now(),
                                        'http://onet.pl', max_links=400)
        task.stop()
        assert Task.objects.get(id=task.id).finished

        resp = self.client.get(reverse('stop_task', kwargs={'task_id': task.id}), follow=True)
        assert Task.objects.get(id=task.id).finished
        assert 'Task already finished!' in self.messages(resp)

    def test_get_data(self, client):
        task = Task.objects.create_task(self.user, 'task', 5, timezone.now(),
                                        'http://onet.pl', max_links=400)

        resp = self.client.get(reverse('get_data', kwargs={'task_id': task.id}), follow=True)
        assert resp.status_code == 200
        old_date = Task.objects.get(id=task.id).last_data_download

        resp = self.client.get(reverse('get_data', kwargs={'task_id': task.id}), follow=True)
        assert resp.status_code == 200
        new_date = Task.objects.get(id=task.id).last_data_download
        assert new_date > old_date

    def test_get_data_failed_incorrect_id(self, client):
        resp = self.client.get(reverse('get_data', kwargs={'task_id': '500'}), follow=True)
        assert resp.status_code == 404

    def test_edit_user_data_get(self, client):
        resp = self.client.get(reverse('edit_user_data', kwargs={'username': 'test_user'}), follow=True)
        assert resp.status_code == 200

    def test_edit_user_data_post(self, client):
        resp = self.client.post(reverse('edit_user_data', kwargs={'username': 'test_user'}), {'last_name': 'last', 'first_name': 'first',
                                                            'email': 'mail@mail.pl'}, follow=True)
        assert resp.status_code == 200
        assert 'Your data updated!' in self.messages(resp)

    def test_show_quota(self, client):
        resp = self.client.get(reverse('show_quota'), follow=True)
        assert resp.status_code == 200

    def messages(self, resp):
        return [msg.message for msg in resp.context['messages'].__iter__()]