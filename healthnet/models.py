import datetime
import json

from django.core.urlresolvers import reverse
from django.db import models

from healthnet.core.enumfield import EnumField

States = EnumField("Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware",
                   "District of Columbia", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
                   "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
                   "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey",
                   "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
                   "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah",
                   "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming")


class Hospital(models.Model):
    """
    Hospital Model
    """
    name = models.CharField(max_length=255)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, default="")
    city = models.CharField(max_length=255)
    state = models.IntegerField(choices=States.get_choices())
    zipcode = models.CharField(max_length=255)

    def has_user(self, user):
        for u in self.patient_set.all():
            if user.pk == u.pk:
                return True
        for u in self.nurse_set.all():
            if user.pk == u.pk:
                return True
        for u in self.doctor_set.all():
            if user.pk == u.pk:
                return True
        for u in self.administrator_set.all():
            if user.pk == u.pk:
                return True
        return False

    def get_address_str(self):
        return '%s%s, %s, %s %s' % \
               (self.address_line_1, self.address_line_2, self.city, States.get_str(self.state), self.zipcode)

    def __unicode__(self):
        return '%s (%s, %s)' % (self.name, self.city, States.get_str(self.state))

    def __str__(self):
        return self.__unicode__()


# Import External Models
from healthnet.core.users.user import User, UserType
from healthnet.core.users.patient import Patient, Gender, MaritalStatus
from healthnet.core.users.doctor import Doctor
from healthnet.core.users.nurse import Nurse
from healthnet.core.users.administrator import Administrator
from healthnet.core.logging import LogEntry, LogLevel, Logging


class Calendar(models.Model):
    @staticmethod
    def get_appointments_for_attendee_for_day(attendee: User, date: datetime):
        """
        Gets a list of Appointments for the selected user and date
        :param attendee: User selected
        :param date: Date selected
        :return: apts: list of appointments
        """
        apts = []
        for apt in attendee.appointment_set.all():
            if date.date() == apt.tstart.date():
                apts += [apt]
        return apts

    @staticmethod
    def get_appointments_json(attendee: User):
        """
        Get the appointments that the current user is in
        :param attendee: User currently logged in
        :return:
        """
        apts = []
        for apt in attendee.appointment_set.all():
            apts += [
                {
                    'id': apt.pk,
                    'title': apt.name,
                    'description': apt.description,
                    'url': reverse('edit_appointment', kwargs={'pk': apt.pk}),
                    'start': apt.tstart.astimezone().strftime("%c"),
                    'end': apt.tend.astimezone().strftime("%c"),
                }
            ]
        return json.dumps(apts)

    @staticmethod
    def create_appointment(attendees, name, desc, start, end):
        """
        Creates an appointment
        :param attendees: people(doctors, patients) that are involved
        :param name: name of appointment
        :param desc: description of appointment
        :param start: start time
        :param end: end time
        :return: apt: appointment object
        """
        apt = Appointment.objects.create(name=name, description=desc, attendees=attendees, tstart=start, tend=end)
        if Calendar.has_conflict(attendees, start, end):
            return False, 'Appointment could not be created because there was a conflict.'
        apt.save()

        Logging.info("Created appointment with pk '%s'" % str(apt.pk))

        return True, apt

    @staticmethod
    def update_appointment(appointment, attendees=None, name=None, desc=None, start=None, end=None):
        """
        Updates an existing appointment
        :param appointment: the appointment to be updated
        :param attendees: the new people involved
        :param name: the new name of the appointment
        :param desc: the new description
        :param start: the new start time
        :param end: the new end time
        :return: the updated appointment object
        """
        if type(appointment) == int:
            appointment = Appointment.objects.get(pk=appointment)

        if type(appointment) != Appointment:
            return False, 'Appointment could not be updated by the provided appointment is not an appointment'

        if attendees is not None:
            appointment.attendees = attendees
        if name is not None:
            appointment.name = name
        if desc is not None:
            appointment.desc = desc
        if start is not None:
            appointment.start = start
        if end is not None:
            appointment.end = end

        Logging.info("Updated appointment with pk '%s'" % str(appointment.pk))
        return True, 'Appointment updated'

    @staticmethod
    def remove_appointment(appointment):
        """
        remove the given appointment
        :param appointment: appointment to be removed
        :return: Boolean: True is it was deleted, False if it was not
        """
        if type(appointment) == int:
            appointment = Appointment.objects.get(pk=appointment)

        if type(appointment) != Appointment:
            return False, 'Appointment could not be updated by the provided appointment is not an appointment'

        appointment.delete()

        Logging.info("Deleted appointment named '%s' with pk '%s'" % (appointment.name, str(appointment.pk)))

        return True, 'Appointment deleted'

    @staticmethod
    def has_conflict(attendees, start, end, ignore_apt=None):
        """
        Checks to see if an appointment conflicts with any already scheduled
        :param attendees: people involved in appointment to be checked
        :param start: start of appointment to be checked
        :param end: end of appointment to be checked
        :param ignore_apt: any appointments that can be ignored
        :return: True if there is a conflict, False if there is not
        """
        attendees = set(attendees)

        for apt in Appointment.objects.all():
            if ignore_apt is not None and apt.pk == ignore_apt.pk:
                continue

            if set(apt.attendees.all()).intersection(attendees):
                if (apt.tstart > start) and (apt.tstart < end) or \
                                (apt.tend > start) and (apt.tstart < end) or \
                                (apt.tstart < start) and (apt.tend > end):
                    return True
        return False


class Appointment(models.Model):
    """
    Appointment model
    """
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    tstart = models.DateTimeField()
    tend = models.DateTimeField()
    attendees = models.ManyToManyField(User)

    def has_conflict(self):
        return Calendar.has_conflict(self.attendees.all(), self.tstart, self.tend, self)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode__()


class Prescription(models.Model):
    """
    Prescription Model
    """
    patient = models.OneToOneField('Patient')
    doctor = models.OneToOneField('Doctor')

    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, default="")
    city = models.CharField(max_length=255)
    state = models.IntegerField(choices=States.get_choices())
    zipcode = models.CharField(max_length=255)

    name = models.CharField(max_length=255)
    expiration_date = models.DateField()
    refills = models.IntegerField()

    def get_address_str(self):
        return '%s%s, %s, %s %s' % \
               (self.address_line_1, self.address_line_2, self.city, States.get_str(self.state), self.zipcode)


class MedicalRecord(models.Model):
    """
    MedicalRecord Model
    """
    pass
