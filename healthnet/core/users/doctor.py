from django.db import models

from healthnet.core.users.user import User


class Doctor(User):
    """
    A doctor
    """
    hospitals = models.ManyToManyField('Hospital', blank=True)
    User.is_doctor = models.BooleanField(default=True)

    def get_appointments(self):
        from healthnet.core.calendar import Appointment
        return Appointment.objects.filter(attendees=User.objects.get(pk=self.pk))

    def get_patients(self):
        from healthnet.core.users.patient import Patient
        return Patient.objects.filter(primary_care_provider=self)

    def get_patient_users(self):
        from healthnet.core.users.patient import Patient
        users = None
        for p in Patient.objects.filter(primary_care_provider=self):
            if users is None:
                users = User.objects.filter(pk=p.pk)
            else:
                users |= User.objects.filter(pk=p.pk)
        return users

    def get_hospitals(self):
        return self.hospitals.all()

    @staticmethod
    def get_approved():
        return Doctor.objects.filter(is_pending=False)
