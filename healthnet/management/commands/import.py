import argparse
from datetime import date as date_type, datetime
from datetime import datetime as datetime_type

import django
from django.core.management import BaseCommand

from healthnet.core.calendar import Calendar
from healthnet.core.healthnet_porter import HealthNetImport
from healthnet.core.hospital import Hospital
from healthnet.core.logging import Logging
from healthnet.core.prescription import Prescription
from healthnet.core.result import Result
from healthnet.core.users.patient import Patient
from healthnet.core.users.user import UserType, User


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-f', nargs=1, type=argparse.FileType('r'))

    def handle(self, *args, **options):
        if options['f'] is None:
            print('Usage: manage.py import -f <json_filename>.')
            return

        imported_json = options['f'][0].read()

        importer = HealthNetImport(imported_json, self.add_hospital, self.add_admin, self.add_doctor, self.add_nurse,
                                   self.add_patient, self.add_appointment, self.add_prescription, self.add_test,
                                   self.add_log_entry)
        importer.import_all()

    def add_hospital(self, name: str, addr: str):
        hospital = Hospital.objects.create(name=name, address_line_1=addr, city="", state=0, zipcode="")
        hospital.save()
        return hospital.pk

    def add_admin(self, username: str, password_hash: str, first_name: str, last_name: str, middle_name: str,
                  dob: date_type, addr: str, email: str, phone: str, primary_hospital_id: int, hospital_ids: list):
        b, user = User.create_user(username=username, password="", usertype=UserType.Administrator, email=email, first_name=first_name, last_name=last_name, print_stdout=False)
        user.password = password_hash
        user.save(update_fields=["password"])
        user.save()
        user = user.get_typed_user()
        user.hospital_id = primary_hospital_id
        user.is_pending = False
        user.save()
        return user.pk

    def add_doctor(self, username: str, password_hash: str, first_name: str, last_name: str, middle_name: str,
                   dob: date_type, addr: str, email: str, phone: str, hospital_ids: list, patient_ids: list):
        bool, user = User.create_user(username=username, password="", usertype=UserType.Doctor, email=email, first_name=first_name, last_name=last_name, print_stdout=False)
        user.password = password_hash
        user.save(update_fields=["password"])
        user.is_pending = False
        user.save()
        return user.get_typed_user().pk

    def add_nurse(self, username: str, password_hash: str, first_name: str, last_name: str, middle_name: str,
                  dob: date_type, addr: str, email: str, phone: str, primary_hospital_id: list, doctor_ids: list):
        b, user = User.create_user(username=username, password="", usertype=UserType.Nurse, email=email, first_name=first_name, last_name=last_name, print_stdout=False)
        user.password = password_hash
        user.save(update_fields=["password"])
        user = user.get_typed_user()
        user.hospital_id = primary_hospital_id
        user.is_pending = False
        user.save()
        return user.pk

    def add_patient(self, username: str, password_hash: str, first_name: str, middle_name: str, last_name: str,
                    dob: date_type, addr: str, email: str, phone: str, emergency_contact: str, eye_color: str,
                    bloodtype: str, height: int, weight: int, primary_hospital_id: int, primary_doctor_id: int,
                    doctor_ids: list):
        b, user = User.create_user(username=username, password="password", usertype=UserType.Patient, email=email, first_name=first_name, last_name=last_name, primary_care_provider_id=primary_doctor_id, hospital_id=primary_hospital_id, health_insurance_number=self.generate_insurance_number(), print_stdout=False)
        user.password = password_hash
        user.save(update_fields=["password"])
        user = user.get_typed_user()
        user.height = height
        user.weight = weight
        user.cholesterol = 0
        user.dob = dob
        user.home_phone = phone
        user.emergency_contact_name = emergency_contact
        user.is_pending = False
        user.save()
        return user.pk

    def add_appointment(self, start: datetime_type, end: datetime_type, location: str, description: str,
                        doctor_ids: list, nurse_ids: list, patient_ids: list):

        if doctor_ids is None:
            doctor_ids = []

        if nurse_ids is None:
            nurse_ids = []

        if patient_ids is None:
            patient_ids = []

        attendees = User.objects.filter(pk__in=(doctor_ids + nurse_ids + patient_ids))
        b, apt = Calendar.create_appointment(name=description, attendees=attendees, creator=attendees[0] if len(attendees) > 0 else None, desc=description, start=django.utils.timezone.make_aware(start), end=django.utils.timezone.make_aware(end))

    def add_prescription(self, name: str, dosage: int, notes: str, doctor_id: int, patient_id: int):
        prescription = Prescription.objects.create(name=name, refills=dosage, description=notes, doctor_id=doctor_id, patient_id=patient_id, state=0, expiration_date=datetime.now())
        prescription.save()
        return prescription.pk

    def add_test(self, name: str, date: date_type, description: str, results: str, released: bool, doctor_id: int,
                 patient_id: int):
        result = Result.objects.create(test_type=name, test_date=date, description=description, comment=results, is_released=released, doctor_id=doctor_id, patient_id=patient_id)
        result.save()
        return result.pk

    def add_log_entry(self, user_id: int, request_method: str, request_secure: bool, request_addr: str,
                      description: str, hospital_id: int):
       Logging.info(description, print_stdout=False)

    def generate_insurance_number(self):
        # FORMAT NO DOES HAS HEALTH INSURANCE NUMBERS :'(
        import string
        import random

        num = ''.join(random.sample(string.ascii_uppercase, 1)).join(random.sample(string.ascii_uppercase + string.digits, 11))

        if Patient.objects.filter(health_insurance_number=num).count() > 0:
            return self.generate_insurance_number()

        return num