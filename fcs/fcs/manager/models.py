from django.core.exceptions import ValidationError
from django.db import models

from django.utils import timezone
import django.contrib.auth.models


class UserManager(django.contrib.auth.models.BaseUserManager):

    def create_user(self, username, email, password):
        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.is_active = False
        user.save(using=self._db)
        quota = Quota.objects.create(user=user)
        quota.save()
        return user

    def create_superuser(self, username, email, password):
        user = self.create_user(username=username, email=self.normalize_email(email), password=password)
        user.is_active = True
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(django.contrib.auth.models.AbstractUser):
    objects = UserManager()

    def __unicode__(self):
        return "User %s" % self.username


class Quota(models.Model):
    max_priority = models.IntegerField(default=10)
    priority_pool = models.IntegerField(default=100)
    max_tasks = models.IntegerField(default=5)
    link_pool = models.IntegerField(default=1000000)
    max_links = models.IntegerField(default=100000)
    user = models.OneToOneField(User)

    def __unicode__(self):
        return "User %s quota" % self.user.__unicode__()


class QuotaException(Exception):
    pass


class CrawlingType(models.Model):
    TEXT = 0
    PICTURES = 1
    LINKS = 2
    CRAWLING_TYPES_CHOICES = (
        (0, 'TEXT'),
        (1, 'PICTURES'),
        (2, 'LINKS')
    )
    type = models.IntegerField(max_length=1, choices=CRAWLING_TYPES_CHOICES)

    def __unicode__(self):
        return self.get_type_display()


class TaskManager(models.Manager):

    @staticmethod
    def create_task(user, name, priority, expire, types, whitelist, blacklist='', max_links=1000):
        """Return new task.

        Raises QuotaException when user quota is exceeded.
        """
        if user.quota.max_priority < priority:
            raise QuotaException('Task priority exceeds user quota!')
        if user.quota.max_tasks == user.task_set.filter(finished=False).count():
            raise QuotaException('User has too many opened tasks!')
        if user.quota.max_links < max_links:
            raise QuotaException('Task link limit exceeds user quota!')
        task = Task(user=user, name=name, whitelist=whitelist, blacklist=blacklist, max_links=max_links,
                    expire_date=expire, priority=priority)
        task.save()
        task.type.add(*list(types))
        task.save()
        return task


class Task(models.Model):
    """Class representing crawling tasks defined by users"""
    user = models.ForeignKey(User, null=False)
    name = models.CharField(max_length=100, null=False, unique=True)
    priority = models.IntegerField(default=1, null=False)
    whitelist = models.CharField(max_length=250, null=False)
    blacklist = models.CharField(max_length=250, null=False)
    max_links = models.IntegerField(default=1000, null=False)
    expire_date = models.DateTimeField(null=False)
    type = models.ManyToManyField(CrawlingType)
    active = models.BooleanField(default=True)
    finished = models.BooleanField(default=False)
    created = models.DateTimeField(default=timezone.now, null=False)

    objects = TaskManager()

    def change_priority(self, priority):
        """Set task priority.

        Task with higher priority crawls more links at the same time than those with lower priority.
        Task priority cannot exceed quota of user which owns this task. In other case QuotaException is raised.
        """
        if self.user.quota.max_priority < priority:
            raise QuotaException('Task priority exceeds user quota!')
        self.priority = priority
        self.save()

    def pause(self):
        """Pause task.

        Paused task does not crawl any links until it is resumed.
        """
        self.active = False
        self.save()

    def resume(self):
        """Resume task.

        Task becomes active so it can crawl links.
        """
        self.active = True
        self.save()

    def stop(self):
        """Mark task as finished.

        Finished tasks do not count to user max_tasks quota.
        """
        self.finished = True
        self.save()

    def feedback(self, score_dict):
        """Process feedback from client

        Update crawling process in order to satisfy client expectations
        """
        #TODO: implement
        pass

    def __unicode__(self):
        return "Task %s of user %s" % (self.name, self.user)




