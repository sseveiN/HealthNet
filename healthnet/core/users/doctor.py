from django.db import models

from healthnet.core.users.patient import Patient
from healthnet.core.users.user import User


class Doctor(User):
    """
    A doctor
    """
    hospitals = models.ManyToManyField('Hospital', blank=True)
    User.is_doctor = models.BooleanField(default=True)

    def get_patients(self):
        return Patient.objects.filter(doctors=self)

    def get_hospitals(self):
        return self.hospitals.all().order_by('name')