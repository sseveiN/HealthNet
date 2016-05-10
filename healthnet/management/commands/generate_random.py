import string
import random
from datetime import datetime, timedelta

from django.core.management import BaseCommand

import names
from healthnet.core.calendar import Calendar
from healthnet.core.hospital import Hospital
from healthnet.core.prescription import Prescription
from healthnet.core.result import Result
from healthnet.core.users.doctor import Doctor
from healthnet.core.users.patient import Patient
from healthnet.core.users.user import User, UserType


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-n', nargs=1, type=int)

    def handle(self, *args, **options):
        if options['n'] is None:
            print('Usage: manage.py import -n <number_of_models_to_gen>.')
            return

        number = options['n'][0]

        for _ in range(number):
            self.gen_hospital()
            self.gen_admin()
            self.gen_doctor()
            self.gen_nurse()
            self.gen_patient()
            self.gen_result()
            self.gen_prescription()
            self.gen_apt()

    def random_string(self, sample_set, length, length_max=None):
        if length_max is None:
            length_max = length

        return ''.join([random.choice(sample_set) for _ in range(random.randint(length, length_max))])

    def random_alpha(self, length, length_max=None):
        return self.random_string(string.ascii_letters, length, length_max)

    def random_alphaspace(self, length, length_max=None):
        return self.random_string(string.ascii_letters + ' ', length, length_max)

    def random_alphanum(self, length, length_max=None):
        return self.random_string(string.ascii_letters + string.digits, length, length_max)

    def random_email(self):
        return self.random_alphanum(5, 15) + '@' + self.random_alphanum(5, 15) + '.com'

    def random_hospital(self, n=1):
        return Hospital.objects.order_by('?')[:n]

    def random_doctor(self, n=1):
        return Doctor.objects.order_by('?')[:n]

    def random_patient(self, n=1):
        return Patient.objects.order_by('?')[:n]

    def random_state(self):
        return random.randint(0, 51)

    def random_bool(self):
        return bool(random.randint(0, 1))

    def random_zip(self):
        return self.random_string(string.digits, 5)

    def random_insurance_number(self):
        num = ''.join(random.sample(string.ascii_uppercase, 1)).join(
            random.sample(string.ascii_uppercase + string.digits, 11))

        if Patient.objects.filter(health_insurance_number=num).count() > 0:
            return self.random_insurance_number()

        return num

    def random_date(self):
        year = random.randint(1950, 2015)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        return datetime(year, month, day)

    def gen_hospital(self):
        hosp = Hospital.objects.create(
            name=self.random_alpha(5, 15),
            address_line_1=self.random_alpha(5, 15),
            address_line_2="",
            city=self.random_alpha(5, 15),
            state=self.random_state(),
            zipcode=self.random_zip()
        )
        hosp.save()

    def gen_admin(self):
        b, admin = User.create_user(username=self.random_alphanum(5, 20), password="password", usertype=UserType.Administrator, email=self.random_email(),
                         first_name=names.get_first_name(), last_name=names.get_last_name(), print_stdout=False)
        admin = admin.get_typed_user()
        admin.hospital = self.random_hospital().first()
        admin.is_pending = False
        admin.save()

    def gen_doctor(self):
        b, doc = User.create_user(username=self.random_alphanum(5, 20), password="password", usertype=UserType.Doctor, email=self.random_email(),
                         first_name=names.get_first_name(), last_name=names.get_last_name(), print_stdout=False)

        doc = doc.get_typed_user()
        doc.hospitals = self.random_hospital(random.randint(1, 10))
        doc.is_pending = False
        doc.save()

    def gen_nurse(self):
        b, nurse = User.create_user(username=self.random_alphanum(5, 20), password="password", usertype=UserType.Nurse, email=self.random_email(),
                     first_name=names.get_first_name(), last_name=names.get_last_name(), print_stdout=False)
        nurse = nurse.get_typed_user()
        nurse.hospital = self.random_hospital().first()
        nurse.is_pending = False
        nurse.save()

    def gen_patient(self):
        pat = Patient.create_patient(
            username=self.random_alphanum(5, 20),
            health_id=self.random_insurance_number(),
            email=self.random_email(),
            password="",
            first_name=names.get_first_name(),
            last_name=names.get_last_name(),
            dob=self.random_date(),
            hospital=self.random_hospital().first(),
            pcp=self.random_doctor().first()
        )
        pat = pat.get_typed_user()
        pat.visits = random.randint(0, 13337)
        pat.average_visit_length = random.randint(0, 1034592034)
        pat.is_admitted = self.random_bool()
        pat.save()

    def gen_apt(self):
        creator = self.random_doctor().first()
        attendees = User.generify_queryset(creator.get_patients())
        attendees |= User.objects.filter(pk=creator.pk)
        start = self.random_date() + timedelta(minutes=random.randint(0, 10000))
        end = start + timedelta(minutes=30)
        Calendar.create_appointment(
            creator=creator,
            attendees=attendees,
            name=self.random_alpha(10, 30),
            desc=self.random_alphaspace(15, 100),
            start=start,
            end=end
        )

    def gen_prescription(self):
        Prescription.objects.create(
            name=self.random_alpha(5, 15),
            issue_date=self.random_date(),
            expiration_date=self.random_date(),
            refills=random.randint(0, 1337),
            description=self.random_alphaspace(15, 100),
            patient=self.random_patient().first(),
            doctor=self.random_doctor().first(),
            address_line_1=self.random_alpha(5, 15),
            address_line_2="",
            city=self.random_alpha(5, 15),
            state=self.random_state(),
            zipcode=self.random_zip()
        )

    def gen_result(self):
        Result.objects.create(
            patient=self.random_patient().first(),
            doctor=self.random_doctor().first(),
            test_date=self.random_date(),
            test_type=self.random_alpha(10, 30),
            release_date=self.random_date(),
            description=self.random_alphaspace(15, 100),
            comment=self.random_alphaspace(15, 100),
            is_released=self.random_bool(),
            file=None
        )
