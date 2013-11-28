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
    mock_field = models.IntegerField()
    user = models.OneToOneField(User)

    def __unicode__(self):
        return "User %s quota" % self.user.__unicode__()









