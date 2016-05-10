from datetime import datetime

import django
from django.db import models


class Result(models.Model):
    """
    Test Result Model
    """
    patient = models.ForeignKey('Patient', unique=False, blank=True, null=True)
    doctor = models.ForeignKey('Doctor', unique=False, blank=True, null=True)
    test_date = models.DateField()
    test_type = models.CharField(max_length=255)
    release_date = models.DateField(blank=True, null=True)
    description = models.CharField(max_length=255)
    comment = models.CharField(max_length=255)
    is_released = models.BooleanField(default=False)
    file = models.FileField(upload_to='results', blank=True, null=True)

    # def create_result(doctor):
    #    time = datetime.now()
    #    result = Result.objects.create(patient=None, doctor=doctor, test_date=time, release_date=None,
    #                                   description=None, is_released=None)
    #    result.save()
    #    return True, result

    def release_result(self):
        """
        Release a result
        :return: Whether or not the result was released
        """
        self.release_date = django.utils.timezone.now()
        self.is_released = True
        self.save()
        return True
