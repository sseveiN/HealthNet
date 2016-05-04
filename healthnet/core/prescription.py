import django
from django.db import models

from healthnet.models import States


class Prescription(models.Model):
    """
    Prescription Model
    """
    patient = models.ForeignKey('Patient', unique=False, blank=True, null=True)
    doctor = models.ForeignKey('Doctor', unique=False, blank=True, null=True)

    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, default="")
    city = models.CharField(max_length=255)
    state = models.IntegerField(choices=States.get_choices())
    zipcode = models.CharField(max_length=5)

    name = models.CharField(max_length=255)
    issue_date = models.DateField(default=django.utils.timezone.now())
    expiration_date = models.DateField()
    refills = models.IntegerField()

    description = models.CharField(max_length=255)

    def get_address_str(self):
        """
        Get the string representation of an address
        :return: The string representation of an address
        """
        return '%s%s, %s, %s %s' % \
               (self.address_line_1, self.address_line_2, self.city, States.get_str(self.state), self.zipcode)
