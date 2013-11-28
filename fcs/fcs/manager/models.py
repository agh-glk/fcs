from django.db import models
from django.contrib.auth.models import User

class FakeModel():

    def fake_method(self):
            return True

class Quota(models.Model):
    mock_field = models.IntegerField()

class ClientData(models.Model):
    user = models.OneToOneField(User)
    quota = models.OneToOneField(Quota)

    def __unicode__(self):
        return self.user.__unicode__()






