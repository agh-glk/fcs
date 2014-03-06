from django.db import models
from userena.models import UserenaBaseProfile
from fcs.manager.models import User


class UserProfile(UserenaBaseProfile):
    """
    Additional user data. required by Userena plugin.
    """
    user = models.OneToOneField(User, unique=True, verbose_name='user', related_name='user_profile')