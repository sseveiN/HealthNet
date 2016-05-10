from django.db import models

from healthnet.core.users.user import User


class Doctor(User):
    """
    A doctor
    """
    hospitals = models.ManyToManyField('Hospital', blank=True)
    User.is_doctor = models.BooleanField(default=True)

    def get_appointments(self):
        """
        Get all the appointments for this doctor
        :return: A queryset of appointments
        """
        from healthnet.core.calendar import Appointment
        return Appointment.objects.filter(attendees=User.objects.get(pk=self.pk))

    def get_patients(self):
        """
        Get all the patients for this doctor
        :return: A queryset of patients
        """
        from healthnet.core.users.patient import Patient
        return Patient.objects.filter(primary_care_provider=self)

    def get_patient_users(self):
        """
        Get the users patients as a set of Users
        :return: A queryset of users
        """
        return User.generify_queryset(self.get_patients())

    def get_hospitals(self):
        """
        Get all the hospitals for this doctor
        :return: A queryset of hospitals
        """
        return self.hospitals.all()

    @staticmethod
    def get_approved():
        """
        Get all the approved doctors
        :return: A queryset of doctors
        """
        return Doctor.objects.filter(is_pending=False)
