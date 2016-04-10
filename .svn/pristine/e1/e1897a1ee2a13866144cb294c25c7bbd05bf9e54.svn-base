from django.db import models

from healthnet.core.users.user import User, UserType


class Administrator(User):
    """
    An Administrator
    """
    User.is_admin = models.BooleanField(default=True)
