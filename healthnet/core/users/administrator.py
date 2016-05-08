from django.db import models

from healthnet.core.users.user import User


class Administrator(User):
    """
    An Administrator
    """
    User.is_admin = models.BooleanField(default=True)

    hospital = models.ForeignKey('Hospital', unique=False, blank=True, null=True)

    def get_hospitals(self):
        return [self.hospital]

    def get_patients(self):
        from healthnet.core.users.patient import Patient
        return Patient.objects.all()

    def get_nurses(self):
        from healthnet.core.users.nurse import Nurse
        return Nurse.objects.filter(hospital=self.hospital)

    def get_doctors(self):
        from healthnet.core.users.doctor import Doctor
        return Doctor.objects.filter(hospital=self.hospital)

