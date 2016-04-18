from django.db import models

from healthnet.core.users.patient import Patient
from healthnet.core.users.user import User, UserType


class Administrator(User):
    """
    An Administrator
    """
    User.is_admin = models.BooleanField(default=True)
    hospitals = models.ForeignKey('Hospital', null=True, blank=True)

    def get_patients(self):
        return Patient.objects.all()
