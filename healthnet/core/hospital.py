from django.db import models

from healthnet.core.users.user import User
from healthnet.core.users.administrator import Administrator
from healthnet.core.users.nurse import Nurse
from healthnet.core.users.patient import Patient

from healthnet.models import States


class Hospital(models.Model):
    """
    Hospital Model
    """

    name = models.CharField(max_length=255)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, default="")
    city = models.CharField(max_length=255)
    state = models.IntegerField(choices=States.get_choices())
    zipcode = models.CharField(max_length=5)

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