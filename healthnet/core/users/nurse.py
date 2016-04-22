from django.db import models

from healthnet.core.users.user import User


class Nurse(User):
    """
    A nurse
    """
    User.is_nurse = models.BooleanField(default=True)
    doctors = models.ManyToManyField('Doctor', blank=True)
    hospitals = models.ForeignKey('Hospital', null=True, blank=True)

    def get_patients(self):
        if self.hospitals is None:
            return None
        if self.hospitals.patient_set is None:
            return None
        return self.hospitals.patient_set.all()
