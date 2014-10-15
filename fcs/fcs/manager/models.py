import json
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.aggregates import Sum

from django.utils import timezone
import django.contrib.auth.models
import requests
from requests.exceptions import ConnectionError
from rest_framework import status
from userena.signals import activation_complete
from oauth2_provider.models import Application
from fcs.backend.utils import changed_fields


class UserManager(django.contrib.auth.models.BaseUserManager):
    """
    Accessed by 'User.objects', provides methods for creation of user and his Quota or superuser.
    """

    def create_user(self, username, email, password):
        """
        Creates common FCS user. He has default Quota.
        """
        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.is_active = False
        user.save(using=self._db)
        quota = Quota.objects.create(user=user)
        quota.save()
        return user

    def create_superuser(self, username, email, password):
        """
        Creates FCS superuser. He can use admin panel.
        """
        user = self.create_user(username=username, email=self.normalize_email(email), password=password)
        user.is_active = True
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(django.contrib.auth.models.AbstractUser):
    """
    FCS user class, based on django.contrib.auth.models.AbstractUser. Username, password and email are required.
    Other fields are optional.
    """
    objects = UserManager()

    def __unicode__(self):
        return self.username


class Quota(models.Model):
    """
    Represents limitations in creating tasks. Each user object is connected with his personal quota.
    """
    max_priority = models.IntegerField(default=10)
    max_tasks = models.IntegerField(default=5)
    link_pool = models.IntegerField(default=1000000)
    max_links = models.IntegerField(default=100000)
    urls_per_min = models.IntegerField(default=1000)
    user = models.OneToOneField(User)

    def __unicode__(self):
        return "User %s quota" % self.user.__unicode__()


class QuotaException(Exception):
    """
    Raised when user exceeds limitations defined by Quota object.
    """
    pass


class TaskManager(models.Manager):
    """
    Accessed by 'Task.objects'. Manages creation of Task instance.
    """

    @staticmethod
    def create_task(user, name, priority, expire, start_links, whitelist='*', blacklist='', max_links=1000, mime_type='text/html'):
        """Return new task.

        Raises QuotaException when user quota is exceeded.
        """
        task = Task(user=user, name=name, whitelist=whitelist, blacklist=blacklist, max_links=max_links,
                    expire_date=expire, priority=priority, mime_type=mime_type, start_links=start_links)
        task.clean()
        task.save()
        return task


class Crawler(models.Model):
    """
    Represents crawler unit
    """
    address = models.CharField(max_length=100, unique=True)
    uuid = models.CharField(max_length=100, unique=True)

    def is_alive(self):
        """
        Checks if crawler represented by this object responds for requests
        """
        r = self.send('/alive')
        if r is None:
            return False
        return r.status_code == status.HTTP_200_OK

    def stop(self):
        """
        Sends stop request to crawler represented by this object.

        If crawler doesn't respond this object will be deleted.
        """
        if self.send('/stop', 'post') is None:
            self.delete()

    def kill(self):
        """
        Sends kill request to crawler represented by this object.

        If crawler doesn't respond this object will be deleted.
        """
        if self.send('/kill', 'post') is None:
            self.delete()

    def send(self, path, method='get', data=None):
        """
        Sends request to crawler represented by this object.

        If connection cannot be established (ConnectionError) None will be returned.
        """
        try:
            if method == 'get':
                return requests.get(self.address + path)
            else:
                return requests.post(self.address + path, data)
        except ConnectionError:
            return None


class TaskServer(models.Model):
    """
    Represents server which executes crawling tasks
    """
    address = models.CharField(max_length=100, unique=True)
    urls_per_min = models.IntegerField(default=0)
    uuid = models.CharField(max_length=100, unique=True)

    def is_alive(self):
        """
        Checks if task server represented by this object responds for requests.
        """
        r = self.send('/alive')
        if not r:
            return False
        return r.status_code == status.HTTP_200_OK

    def kill(self):
        """
        Sends kill request to task server represented by this object.

        If server doesn't respond this object will be deleted.
        """
        if not self.send('/kill', 'post'):
            self.delete()

    def send(self, path, method='get', data=None):
        """
        Sends request to task server represented by this object.

        If connection cannot be established (ConnectionError) None will be returned.
        """
        try:
            if method == 'get':
                return requests.get(self.address + path)
            else:
                return requests.post(self.address + path, data)
        except ConnectionError:
            return None

    def delete(self):
        try:
            self.task.autoscale_change = True
            self.task.save()
        finally:
            super(TaskServer, self).delete()


class Task(models.Model):
    """
    Represents crawling tasks defined by users.
    """
    user = models.ForeignKey(User, null=False)
    name = models.CharField(max_length=100, null=False)
    priority = models.IntegerField(default=1, null=False)
    start_links = models.TextField(max_length=1000, null=False)
    whitelist = models.CharField(max_length=250, null=False, blank=True)
    blacklist = models.CharField(max_length=250, null=False, blank=True)
    max_links = models.IntegerField(default=1000, null=False)
    expire_date = models.DateTimeField(null=False)
    mime_type = models.CharField(max_length=250, null=False, default='text/html')
    active = models.BooleanField(default=True)
    finished = models.BooleanField(default=False)
    created = models.DateTimeField(default=timezone.now, null=False)
    last_data_download = models.DateTimeField(null=True, blank=True)
    server = models.OneToOneField(TaskServer, null=True, on_delete=models.SET_NULL)
    last_server_spawn = models.DateTimeField(null=True)
    autoscale_change = models.BooleanField(default=False)

    objects = TaskManager()

    def clean(self):
        if self.finished:
            self.active = False
        if not self.mime_type:
            self.mime_type = 'text/html'
        if not self.whitelist:
            self.whitelist = '*'
        if not self.start_links:
            raise ValidationError('Start links are required')
        self.start_links = ' '.join(self.start_links.split())
        self.whitelist = ' '.join(self.whitelist.split())
        self.blacklist = ' '.join(self.blacklist.split())
        self.mime_type = ' '.join(self.mime_type.split())

        if self.priority <= 0:
            raise ValidationError('Priority must be positive')
        if self.max_links <= 0:
            raise ValidationError('Links amount must be positive')

        if self.user.quota.max_priority < self.priority:
            raise QuotaException('Task priority exceeds user quota! Limit: ' + str(self.user.quota.max_priority))
        if self.pk is None and self.user.quota.max_tasks <= self.user.task_set.filter(finished=False).count():
            raise QuotaException('User has too many opened tasks! Limit: ' + str(self.user.quota.max_tasks))
        if self.user.quota.max_links < self.max_links:
            raise QuotaException('Task link limit exceeds user quota! Limit: ' + str(self.user.quota.max_links))

        links = self.user.task_set.filter(finished=False).exclude(pk=self.pk).aggregate(Sum('max_links'))['max_links__sum']
        if self.user.quota.link_pool < (links + self.max_links if links else self.max_links):
            raise QuotaException("User link pool exceeded! Limit: " + str(self.user.quota.link_pool))

        if [False for link in str(self.start_links).split() if not (link.startswith('http://') or link.startswith('https://'))]:
            raise ValidationError('Invalid protocol in start links! Only http and https are valid.')

    def save(self, *args, **kwargs):
        changed = changed_fields(self)
        if ('server' in changed and 'active' in changed) \
                or (self.server and 'active' in changed) \
                or (self.active and 'server' in changed) \
                or (self.server and self.active and 'priority' in changed):
            self.autoscale_change = True
        super(Task, self).save(*args, **kwargs)
        if any(x in changed for x in ['finished', 'active', 'max_links', 'whitelist', 'blacklist',
                'expire_date', 'mime_type']):
            self.send_update_to_task_server()

    def get_parsed_whitelist(self):
        """
        Returns whitelist converted from user-friendly regex to python regex
        """
        user_regexes = self.whitelist.split()
        python_regexes = ['^' + regex.replace('.', '\.').replace('*', '.*') + '$' for regex in user_regexes]
        return python_regexes

    def get_parsed_blacklist(self):
        """
        Returns blacklist converted from user-friendly regex to python regex
        """
        user_regexes = self.blacklist.split()
        python_regexes = ['^' + regex.replace('.', '\.').replace('*', '.*') + '$' for regex in user_regexes]
        return python_regexes

    def change_priority(self, priority):
        """
        Sets task priority.

        Task with higher priority crawls more links at the same time than those with lower priority.
        Task priority cannot exceed quota of user which owns this task. In other case QuotaException is raised.
        """
        old = self.priority
        self.priority = priority
        try:
            self.clean()
        except Exception as e:
            self.priority = old
            raise e
        self.save()

    def pause(self):
        """
        Pauses task.

        Paused task does not crawl any links until it is resumed. It temporarily releases resources
        used by this task (such as priority)
        """
        self.active = False
        self.save()

    def resume(self):
        """
        Resumes task.

        Task becomes active so it can crawl links. QuotaException may be thrown if user has not enough
        free priority resources to run this task. Then, user should decrease priority of this
        or other active task.
        """
        old = self.active
        self.active = True
        try:
            self.clean()
        except Exception as e:
            self.active = old
            raise e
        self.save()

    def stop(self):
        """
        Marks task as finished.

        Finished tasks cannot be resumed and they do not count to user max_tasks quota.
        """
        self.finished = True
        self.active = False
        self.save()

    def is_waiting_for_server(self):
        """
        Checks if running task has no task server assigned
        """
        return (not self.finished) and (self.server is None)

    def feedback(self, link, rating):
        """
        Process feedback from client.

        Update crawling process in order to satisfy client expectations
        """
        if self.server:
            data = {'link': link, 'rating': rating}
            self.server.send('/feedback', 'post', json.dumps(data))
        pass

    def __unicode__(self):
        return "Task %s of user %s" % (self.name, self.user)

    def send_update_to_task_server(self):
        if self.server:
            data = {'finished': self.finished, 'active': self.active,
                    'max_links': self.max_links, 'whitelist': self.get_parsed_whitelist(),
                    'blacklist': self.get_parsed_blacklist(),
                    'expire_date': str(self.expire_date), 'mime_type': self.mime_type.split()}
            self.server.send('/update', 'post', json.dumps(data))


def create_api_keys(sender, **kwargs):
    """
    Creates Application object, required for working with REST API.
    """
    user = kwargs['user']
    Application.objects.create(user=user, client_type=Application.CLIENT_CONFIDENTIAL,
                               authorization_grant_type=Application.GRANT_PASSWORD)


activation_complete.connect(create_api_keys)


class MailSent(models.Model):
    """
    Information about sent mails, reminding user of crawling data waiting for him.
    """
    tasks = models.ManyToManyField(Task)
    date = models.DateTimeField(null=False)
