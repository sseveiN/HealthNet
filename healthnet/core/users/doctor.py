from django.db import models

from healthnet.core.users.patient import Patient
from healthnet.core.users.user import User


class Doctor(User):
    """
    A doctor
    """
    User.is_doctor = models.BooleanField(default=True)
    nurses = models.ManyToManyField('Nurse', blank=True)
    hospitals = models.ForeignKey('Hospital', null=True, blank=True)

    def get_patients(self):
        return Patient.objects.filter(doctors=self)
