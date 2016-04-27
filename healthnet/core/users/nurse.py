from django.db import models

from healthnet.core.users.user import User
from healthnet.core.users.patient import Patient


class Nurse(User):
    """
    A nurse
    """
    User.is_nurse = models.BooleanField(default=True)
    hospital = models.ForeignKey('Hospital', unique=False, blank=True, null=True)
    doctors = models.ManyToManyField('Doctor', blank=True, null=True)

    def get_patients(self):
        return Patient.objects.filter(hospital=self.hospital)
