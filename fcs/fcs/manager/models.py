from django.db import models
from django.contrib.auth.models import User

class FakeModel():

    def fake_method(self):
            return True

class UserData(models.Model):
    user = models.OneToOneField(User)

    def __unicode__(self):
        return "User %s data" % self.user.__unicode__()


class Quota(models.Model):
    max_priority = models.IntegerField()
    user = models.OneToOneField(User)

    def __unicode__(self):
        return "User %s quota" % self.user.__unicode__()

class QuotaException(Exception):
    pass

class Task(models.Model):
    user = models.ForeignKey(User, null=False)
    name = models.CharField(max_length=100, null=False)
    priority = models.IntegerField(default=1, null=False)
    whitelist = models.CharField(max_length=250, null=False)
    blacklist = models.CharField(max_length=250, null=False)
    max_links = models.IntegerField(default=1000, null=False)
    expire = models.DateTimeField(null=False)
    type = models.CharField(max_length=20, null=False)

    @classmethod
    def create_task(self, user, name, priority, expire, type, whitelist, blacklist='', max_links=1000):
        if user.quota.max_priority < priority:
            raise QuotaException('Task priority exceeds client quota!')
        task = Task.objects.create(user=user, name=name, whitelist=whitelist, blacklist=blacklist, type=type, max_links=max_links, expire=expire, priority=priority)
        task.save()
        return task

    def set_priority(self, priority):
        if self.user.quota.max_priority < priority:
            raise QuotaException('Task priority exceeds client quota!')
        self.priority = priority
        self.save()





