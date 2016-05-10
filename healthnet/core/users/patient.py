from datetime import date, timedelta

import django
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models

from healthnet.core.enumfield import EnumField
from healthnet.core.prescription import Prescription
from healthnet.core.result import Result
from healthnet.core.users.user import User
from healthnet.models import States

Gender = EnumField('Male', 'Female', 'Unspecified')
MaritalStatus = EnumField('Married', 'Living Common Law', 'Widowed', 'Separated', 'Divorced', 'Single', 'Unspecified')


class Patient(User):
    """
    The patient class, containing:
        records, height, weight, cholesterol, date of birth, address, home phone
        work phone, age, sex, marital status, health insurance provider
        health insurance number, doctors, primary care provider, prescriptions
    """
    User.is_patient = models.BooleanField(default=True)
    records = models.ForeignKey('MedicalRecord', blank=True, null=True)
    height = models.IntegerField(validators=[MaxValueValidator(96), MinValueValidator(0)], blank=True,
                                 null=True)  # Height in in
    weight = models.IntegerField(validators=[MaxValueValidator(400), MinValueValidator(0)], blank=True,
                                 null=True)  # Weight in lbs
    cholesterol = models.IntegerField(validators=[MaxValueValidator(300), MinValueValidator(0)], blank=True,
                                      null=True)  # Cholesterol in mg/dL
    dob = models.DateField(blank=True, null=True)
    home_phone = models.CharField(max_length=12, blank=True, null=True)
    work_phone = models.CharField(max_length=12, blank=True, null=True)
    sex = models.IntegerField(choices=Gender.get_choices(), default=Gender.Unspecified, blank=True, null=True)
    marital_status = models.IntegerField(choices=MaritalStatus.get_choices(), default=MaritalStatus.Unspecified,
                                         blank=True, null=True)
    health_insurance_provider = models.CharField(max_length=30, blank=True,
                                                 null=True)  # All the provider codes ive seen are 5 + 10 numbers
    health_insurance_number = models.CharField(max_length=12,
                                               unique=True, validators=[
            RegexValidator(regex='^[a-zA-z]{1}[a-zA-z0-9]{11}$',
                           message='Health insurance alphanumeric beginning with a letter.')])  # All the insurance numbers ive seen are 5 + 5 characters
    primary_care_provider = models.ForeignKey('Doctor', related_name="primary_care_provider", unique=False)
    prescriptions = models.ForeignKey('Prescription', related_name="patient_prescriptions", blank=True, null=True)

    hospital = models.ForeignKey('Hospital', unique=False)
    is_admitted = models.BooleanField(default=False)
    last_admit_date = models.DateTimeField(blank=True, null=True)

    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True, default="")
    city = models.CharField(max_length=255, blank=True)
    state = models.IntegerField(choices=States.get_choices(), default=1)
    zipcode = models.CharField(max_length=5, blank=True)

    next_of_kin = models.CharField(max_length=255, blank=True)
    emergency_contact = models.CharField(max_length=255, blank=True)
    emergency_contact_number = models.CharField(max_length=12, blank=True)

    is_pending = False

    # Statistics stuff
    average_visit_length = models.IntegerField(default=0)  # seconds
    visits = models.IntegerField(default=0)

    @staticmethod
    def create_patient(health_id, email, username, password, first_name, last_name, dob, hospital, pcp):
        patient = Patient(health_insurance_number=health_id, email=email, username=username, password=password,
                          first_name=first_name, last_name=last_name, dob=dob, hospital=hospital,
                          primary_care_provider=pcp)
        patient.is_patient = True
        patient.is_pending = False
        patient.save()
        return patient

    def get_test_results(self, released=True):
        return Result.objects.filter(patient=self, is_released=released)

    def get_average_visit_length_str(self):
        return timedelta(seconds=self.average_visit_length)

    def get_appointments(self):
        from healthnet.core.calendar import Appointment
        return Appointment.objects.filter(attendees=User.objects.get(pk=self.pk))

    def get_hospitals(self):
        return [self.hospital]

    def get_prescriptions(self):
        return Prescription.objects.filter(patient=self)

    def get_sex_str(self):
        return Gender.get_str(self.sex)

    def get_marital_status_str(self):
        return MaritalStatus.get_str(self.marital_status)

    def get_address_str(self):
        return '%s%s, %s, %s %s' % \
               (self.address_line_1, self.address_line_2, self.city, States.get_str(self.state), self.zipcode)

    def get_age(self):
        today = date.today()
        return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))

    def toggle_admit(self, force=False):
        self.is_admitted = not self.is_admitted or force

        if self.is_admitted:
            # Set last admitted date
            self.last_admit_date = django.utils.timezone.now()

            # Increment visits
            self.visits += 1
        else:
            # Calculate average visit
            if self.last_admit_date is not None:
                self.average_visit_length += (django.utils.timezone.now() - self.last_admit_date).total_seconds()
                self.average_visit_length /= 2

            # Clear admit date
            self.last_admit_date = None

        self.save()

    def transfer(self, hospital):
        self.hospital = hospital
        self.toggle_admit(True)
        self.save()
