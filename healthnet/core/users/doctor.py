from django.db import models

from healthnet.core.users.user import User, UserType


class Doctor(User):
    """
    A doctor
    """
    User.is_doctor = models.BooleanField(default=True)
    patients = models.ManyToManyField('Patient', blank=True)
    nurses = models.ManyToManyField('Nurse', blank=True)
    hospitals = models.ManyToManyField('Hospital', blank=True)

