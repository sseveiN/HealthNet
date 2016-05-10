from django.db import models

from healthnet.core.users.user import User


class Administrator(User):
    """
    An Administrator
    """
    User.is_admin = models.BooleanField(default=True)

    hospital = models.ForeignKey('Hospital', unique=False, blank=True, null=True)

    def get_appointments(self):
        """
        Get all the appointments for this administrator
        :return: A queryset of appointments
        """
        from healthnet.core.calendar import Appointment
        return Appointment.objects.filter(pk=None)

    def get_hospitals(self):
        """
        Get all the hospitals for this administrator
        :return: A queryset of gospitals
        """
        from healthnet.core.hospital import Hospital
        return Hospital.objects.all()

    def get_patients(self):
        """
        Get all the patients for this administrator
        :return: A queryset of patients
        """
        from healthnet.core.users.patient import Patient
        return Patient.objects.all()

    def get_nurses(self):
        """
        Get all the nurses for this administrator
        :return: A queryset of nurses
        """
        from healthnet.core.users.nurse import Nurse
        return Nurse.objects.all()

    def get_doctors(self):
        """
        Get all the doctors for this administrator
        :return: A queryset of doctors
        """
        from healthnet.core.users.doctor import Doctor
        return Doctor.objects.all()
