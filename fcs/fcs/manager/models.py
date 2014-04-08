import json
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.aggregates import Sum
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver

from django.utils import timezone
import django.contrib.auth.models
import requests
from requests.exceptions import ConnectionError
from rest_framework import status
from userena.signals import activation_complete
from oauth2_provider.models import Application


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
    priority_pool = models.IntegerField(default=100)
    max_tasks = models.IntegerField(default=5)
    link_pool = models.IntegerField(default=1000000)
    max_links = models.IntegerField(default=100000)
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
    def create_task(user, name, priority, expire, start_links, whitelist='', blacklist='', max_links=1000, mime_type='text/html'):
        """Return new task.

        Raises QuotaException when user quota is exceeded.
        """
        task = Task(user=user, name=name, whitelist=whitelist, blacklist=blacklist, max_links=max_links,
                    expire_date=expire, priority=priority, mime_type=mime_type, start_links=start_links)
        task.clean()
        task.save()
        return task


# TODO: validate addresses for crawler and server
class Crawler(models.Model):
    """
    Represents crawler unit
    """
    address = models.CharField(max_length=100, unique=True)
    timeouts = models.IntegerField(default=0)
    uuid = models.CharField(max_length=100, unique=True)

    def increase_timeouts(self):
        self.timeouts += 1
        self.save()

    def get_timeouts(self):
        return self.timeouts

    def reset_timeouts(self):
        self.timeouts = 0
        self.save()

    def is_alive(self):
        try:
            r = requests.get(self.address + '/alive')
            return r.status_code == status.HTTP_200_OK
        except ConnectionError:
            return False

    def stop(self):
        try:
            requests.post(self.address + '/stop')
        except ConnectionError:
            self.delete()

    def kill(self):
        try:
            requests.post(self.address + '/kill')
        except ConnectionError:
            self.delete()


class TaskServer(models.Model):
    """
    Represents server which executes crawling tasks
    """
    address = models.CharField(max_length=100, unique=True)
    crawlers = models.ManyToManyField(Crawler)
    uuid = models.CharField(max_length=100, unique=True)

    def is_alive(self):
        try:
            r = requests.get(self.address + '/alive')
            return r.status_code == status.HTTP_200_OK
        except ConnectionError:
            return False

    def kill(self):
        try:
            requests.post(self.address + '/kill')
        except ConnectionError:
            self.delete()


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

    objects = TaskManager()

    def clean(self):
        if self.finished:
            self.active = False
        if not self.mime_type:
            self.mime_type = 'text/html'
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

        priorities = self.user.task_set.filter(active=True).exclude(pk=self.pk).aggregate(Sum('priority'))['priority__sum']
        if self.user.quota.priority_pool < (priorities + self.priority if priorities else self.priority):
            raise QuotaException("User priority pool exceeded! Limit: " + str(self.user.quota.priority_pool))

        links = self.user.task_set.filter(finished=False).exclude(pk=self.pk).aggregate(Sum('max_links'))['max_links__sum']
        if self.user.quota.link_pool < (links + self.max_links if links else self.max_links):
            raise QuotaException("User link pool exceeded! Limit: " + str(self.user.quota.link_pool))

        if [False for link in str(self.start_links).split() if not (link.startswith('http://') or link.startswith('https://'))]:
            raise ValidationError('Invalid protocol in start links! Only http and https are valid.')

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

    def feedback(self, score_dict):
        """
        Process feedback from client.

        Update crawling process in order to satisfy client expectations
        """
        #TODO: implement (should it be here? maybe send request directly to task server?)
        pass

    def __unicode__(self):
        return "Task %s of user %s" % (self.name, self.user)


def create_api_keys(sender, **kwargs):
    """
    Creates Application object, required for working with REST API.
    """
    user = kwargs['user']
    Application.objects.create(user=user, client_type=Application.CLIENT_CONFIDENTIAL,
                               authorization_grant_type=Application.GRANT_PASSWORD)


activation_complete.connect(create_api_keys)


@receiver(post_save, sender=Task, dispatch_uid="server_updater_identifier")
def send_update_to_task_server(sender, **kwargs):
    task = kwargs['instance']
    if task.server:
        data = {'finished': task.finished, 'active': task.active, 'priority': task.priority, 'max_links': task.max_links,
                'whitelist': task.whitelist, 'blacklist': task.blacklist, 'expire_date': str(task.expire_date)}
        requests.post(task.server.address + '/update', json.dumps(data))


class MailSent(models.Model):
    """
    Information about sent mails, reminding user of crawling data waiting for him.
    """
    tasks = models.ManyToManyField(Task)
    date = models.DateTimeField(null=False)
