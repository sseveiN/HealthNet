from django.db import models

from healthnet.core.users.user import User


class Nurse(User):
    """
    A nurse
    """
    User.is_nurse = models.BooleanField(default=True)
    hospital = models.ForeignKey('Hospital', unique=False, blank=True, null=True)

    def get_patients(self):
        return None
