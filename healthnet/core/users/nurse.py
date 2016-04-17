from django.db import models

from healthnet.core.users.user import UserType, User


class Nurse(User):
    """
    A nurse
    """
    User.is_nurse = models.BooleanField(default=True)
    doctors = models.ManyToManyField('Doctor')
    hospitals = models.ForeignKey('Hospital', null=True, blank=True)

    def get_patients(self):
        out = []
        if self.hospitals is None:
            return out
        for hospital in self.hospitals:
            out += hospital.patient_set
        return out

