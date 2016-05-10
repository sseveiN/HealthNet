import operator

from django.db import models

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

    def get_doctors(self):
        """
        Get all doctors in this hospital
        :return: A queryset of doctors
        """
        from healthnet.core.users.doctor import Doctor
        return Doctor.objects.filter(hospitals=self)

    def get_patients(self):
        """
        Get all the patients in this hospital
        :return: A queryset of patients in the hospital
        """
        return Patient.objects.filter(hospital=self)

    def get_visits_and_length(self):
        """
        Get the average number of visits and the average visit length
        :return: A tuple of the average number of visits and the length
        """
        pats = self.get_patients()
        visits, length = [], []
        for p in pats:
            visits += [p.visits]
            length += [p.average_visit_length]
        return visits, length

    def get_popular_prescriptions(self):
        """
        Get popular prescriptions for this hospital
        :return: A dictionary representing prescriptions and the number of times issued
        """
        pats = self.get_patients().all()
        names = {}
        for pat in pats:
            for p in pat.get_prescriptions():
                if p.name not in names:
                    names[p.name] = 0
                names[p.name] += 1
        return sorted(names.items(), key=operator.itemgetter(1))

    def get_average_prescription_length(self):
        """
        Gets the average length of prescriptions at this hospital
        :return: The average length of prescriptions
        """
        pats = self.get_patients().all()
        sum = 0
        count = 0
        for pat in pats:
            for p in pat.get_prescriptions():
                sum += (p.expiration_date - p.issue_date).total_seconds()
                count += 1

        if count == 0:
            return 0

        return sum / count

    def has_user(self, user):
        """
        Checks if a hospital is associated with a user
        :param user: The user to check
        :return: Whether or not the user is associated
        """
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
        """
        Get the address string of this hospital
        :return:
        """
        return '%s%s, %s, %s %s' % \
               (self.address_line_1, self.address_line_2, self.city, States.get_str(self.state), self.zipcode)

    def __unicode__(self):
        """
        :return: The unicode representation of the object
        """
        return '%s (%s, %s)' % (self.name, self.city, States.get_str(self.state))

    def __str__(self):
        """
        :return: The string representation of the object
        """
        return self.__unicode__()
