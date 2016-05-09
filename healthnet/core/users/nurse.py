from django.db import models

from healthnet.core.calendar import Appointment
from healthnet.core.users.user import User


class Nurse(User):
    """
    A nurse
    """
    User.is_nurse = models.BooleanField(default=True)
    hospital = models.ForeignKey('Hospital', unique=False, blank=True, null=True)

    def get_patients(self):
        from healthnet.core.users.patient import Patient
        return Patient.objects.filter(hospital=self.hospital)

    def get_appointments(self):
        apts = None
        for p in self.get_patients():
            for apt in p.get_appointments():
                if apts is None:
                    apts = Appointment.objects.filter(pk=apt.pk)
                else:
                    apts |= Appointment.objects.filter(pk=apt.pk)
        return apts

    def get_attendee_queryset(self):
        a = None
        for d in self.hospital.get_doctors():
            if a is None:
                a = User.objects.filter(pk=d.pk)
            else:
                a |= User.objects.filter(pk=d.pk)
            for p in d.get_patients():
                a |= User.objects.filter(pk=p.pk)
        return a
