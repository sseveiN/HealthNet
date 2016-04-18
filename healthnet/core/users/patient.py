from datetime import date

from django.db import models

from healthnet.core.users.user import User, UserType
from healthnet.core.enumfield import EnumField
from healthnet.models import States

Gender = EnumField('Male', 'Female', 'Unspecified')
MaritalStatus = EnumField('Married', 'LivingCommonLaw', 'Widowed', 'Separated', 'Divorced', 'Single', 'Unspecified')


class Patient(User):
    """
    The patient class, containing:
        records, height, weight, cholesterol, date of birth, address, home phone
        work phone, age, sex, marital status, health insurance provider
        health insurance number, doctors, primary care provider, prescriptions
    """
    User.is_patient = models.BooleanField(default=True)
    records = models.ForeignKey('MedicalRecord', blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)  # Height in cm
    weight = models.IntegerField(blank=True, null=True)  # Weight in lbs
    cholesterol = models.IntegerField(blank=True, null=True)  # Cholesterol in mg/dL
    dob = models.DateField(blank=True, null=True)
    home_phone = models.CharField(max_length=12, blank=True, null=True)
    work_phone = models.CharField(max_length=12, blank=True, null=True)
    sex = models.IntegerField(choices=Gender.get_choices(), default=Gender.Unspecified, blank=True, null=True)
    marital_status = models.IntegerField(choices=MaritalStatus.get_choices(), default=MaritalStatus.Unspecified, blank=True, null=True)
    health_insurance_provider = models.CharField(max_length=15, blank=True, null=True)  # All the provider codes ive seen are 5 + 10 numbers
    health_insurance_number = models.CharField(max_length=10, unique=True)  # All the insurance numbers ive seen are 5 + 5 characters
    doctors = models.ManyToManyField('Doctor', blank=True)
    primary_care_provider = models.ForeignKey('Doctor', related_name="primary_care_provider", blank=True, null=True, unique=False)
    prescriptions = models.ForeignKey('Prescription', related_name="patient_prescriptions", blank=True, null=True)
    hospital = models.ForeignKey('Hospital', null=True, blank=True, default=None)
    is_admitted = models.BooleanField(default=False)

    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, default="")
    city = models.CharField(max_length=255)
    state = models.IntegerField(choices=States.get_choices())
    zipcode = models.CharField(max_length=255)

    is_pending = False

    def get_address_str(self):
        return '%s%s, %s, %s %s' % \
               (self.address_line_1, self.address_line_2, self.city, States.get_str(self.state), self.zipcode)

    def get_age(self):
        today = date.today()
        return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))

    def toggle_admit(self):
        self.is_admitted = not self.is_admitted
        self.save()

    def transfer(self, hospital):
        self.hospital = hospital
        self.is_admitted = True
        self.save()
