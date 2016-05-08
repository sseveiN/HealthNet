from django.db import models

from healthnet.core.users.user import User


class Doctor(User):
    """
    A doctor
    """
    hospitals = models.ManyToManyField('Hospital', blank=True)
    User.is_doctor = models.BooleanField(default=True)

    def get_patients(self):
        from healthnet.core.users.patient import Patient
        return Patient.objects.filter(primary_care_provider=self)

    def get_hospitals(self):
        return self.hospitals.all()

    @staticmethod
    def get_approved():
        return Doctor.objects.filter(is_pending=False)
