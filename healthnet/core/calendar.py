import datetime
import json

import django
from django.core.urlresolvers import reverse
from django.db import models

from healthnet.core.logging import Logging
from healthnet.core.users.user import User


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
        for apt in attendee.get_appointments():
            if date.date() == apt.tstart.date() and not apt.is_in_past():
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
        for apt in attendee.get_appointments().all():
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
    def get_appointments_json_multi(attendees: list, show_info=True):
        """
        Get the appointments that the current user is in
        :param attendees: Users to get appointments for
        :return:
        """
        apts = []
        for attendee in attendees:
            for apt in attendee.get_appointments().all():
                apts += [
                    {
                        'id': apt.pk,
                        'title': apt.name if show_info else "",
                        'description': apt.description if show_info else "",
                        'url': reverse('edit_appointment', kwargs={'pk': apt.pk}) if show_info else "",
                        'start': apt.tstart.astimezone().strftime("%c"),
                        'end': apt.tend.astimezone().strftime("%c"),
                    }
                ]
        return json.dumps(apts)

    @staticmethod
    def create_appointment(attendees, creator, name, desc, start, end):
        """
        Creates an appointment
        :param attendees: people(doctors, patients) that are involved
        :param creator: the creator of the appointment
        :param name: name of appointment
        :param desc: description of appointment
        :param start: start time
        :param end: end time
        :return: conflict, apt: whether or not there was a conflict, appointment object
        """

        if Calendar.has_conflict(attendees, start, end):
            return True, 'Appointment could not be created because there was a conflict.'

        apt = Appointment.objects.create(name=name, description=desc, creator=creator, tstart=start, tend=end)
        apt.attendees = attendees
        apt.save()

        Logging.info("Created appointment with pk '%s'" % str(apt.pk))

        return False, apt

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
    creator = models.ForeignKey(User, related_name="created_appointments", null=True)

    def has_conflict(self):
        """
        Check if the appointment has a conflict with any
        other appointment for all attendees
        :return:
        """
        return Calendar.has_conflict(self.attendees.all(), self.tstart, self.tend, self)

    def is_in_past(self):
        return django.utils.timezone.now() > self.tend

    def __unicode__(self):
        """
        :return: The unicode representation of the object
        """
        return self.name

    def __str__(self):
        """
        :return: The string representation of the object
        """
        return self.__unicode__()