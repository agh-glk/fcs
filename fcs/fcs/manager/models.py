from django.contrib.sites.management import create_default_site
from django.db import models
from django.contrib.auth.models import User
from registration import signals
from threading import Lock
from django.utils import timezone

class UserData(models.Model):
    user = models.OneToOneField(User)

    def __unicode__(self):
        return "User %s data" % self.user.__unicode__()


class Quota(models.Model):
    max_priority = models.IntegerField(default=10)
    max_tasks = models.IntegerField(default=5)
    max_links = models.IntegerField(default=10000)
    user = models.OneToOneField(User)

    def __unicode__(self):
        return "User %s quota" % self.user.__unicode__()


class QuotaException(Exception):
    pass


def activate_user_callback(sender, **kwargs):
    """
    Function creates objects connected with User -
    UserData and Quota after user account is activated.
    """
    user = kwargs['user']
    lock = Lock()
    lock.acquire()
    try:
        if Quota.objects.filter(user=user).count() == 0:
            Quota.objects.create(user=user).save()
        if UserData.objects.filter(user=user).count() == 0:
            UserData.objects.create(user=user).save()
    finally:
        lock.release()


signals.user_activated.connect(activate_user_callback, dispatch_uid="model")


CRAWLING_TYPES_CHOICES = (
    (0, 'TEXT'),
    (1, 'PICTURES'),
    (2, 'LINKS')
)
class CrawlingType(models.Model):
    TEXT = 0
    PICTURES = 1
    LINKS = 2
    type = models.IntegerField(max_length=1, choices=CRAWLING_TYPES_CHOICES)

    def __unicode__(self):
        return self.get_type_display()


class Task(models.Model):
    """Class representing crawling tasks defined by users"""
    user = models.ForeignKey(User, null=False)
    name = models.CharField(max_length=100, null=False)
    priority = models.IntegerField(default=1, null=False)
    whitelist = models.CharField(max_length=250, null=False)
    blacklist = models.CharField(max_length=250, null=False)
    max_links = models.IntegerField(default=1000, null=False)
    expire = models.DateTimeField(null=False)
    type = models.ManyToManyField(CrawlingType)
    active = models.BooleanField(default=True)
    finished = models.BooleanField(default=False)
    created = models.DateTimeField(null=False)

    @classmethod
    def create_task(self, user, name, priority, expire, types, whitelist, blacklist='', max_links=1000):
        """Return new task.

        Raises QuotaException when user quota is exceeded.
        """
        if user.quota.max_priority < priority:
            raise QuotaException('Task priority exceeds user quota!')
        if user.quota.max_tasks == user.task_set.filter(finished=False).count():
            raise QuotaException('User has too many opened tasks!')
        if user.quota.max_links < max_links:
            raise QuotaException('Task link limit exceeds user quota!')
        task = Task.objects.create(user=user, name=name, whitelist=whitelist, blacklist=blacklist,
                                   max_links=max_links, expire=expire, priority=priority, created=timezone.now())
        task.save()
        task.type.add(*list(types))
        task.save()
        return task

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

    def feedback(self,score_dict):
        """Process feedback from client

        Update crawling process in order to satisfy client expectations
        """
        #TODO: implement
        pass

    def __unicode__(self):
        return "Task %s of user %s" % (self.name, self.user)







