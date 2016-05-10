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
        from healthnet.core.users.doctor import Doctor
        return Doctor.objects.filter(hospitals=self)

    def get_patients(self):
        """
        Get all the patients in this hospital
        :return: A list of patients in the hospital
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
        pats = self.get_patients().all()
        names = {}
        for pat in pats:
            for p in pat.get_prescriptions():
                if p.name not in names:
                    names[p.name] = 0
                names[p.name] += 1
        return sorted(names.items(), key=operator.itemgetter(1))

    def get_average_prescription_length(self):
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
