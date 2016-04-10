from django.db import models

from healthnet.core.users.user import UserType, User


class Nurse(User):
    """
    A nurse
    """
    User.is_nurse = models.BooleanField(default=True)
    doctors = models.ManyToManyField('Doctor')
