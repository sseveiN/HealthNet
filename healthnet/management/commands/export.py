import datetime

from django.core.management import BaseCommand

from healthnet.core.healthnet_porter import HealthNetExport
from healthnet.core.hospital import Hospital
from healthnet.core.users.administrator import Administrator
from healthnet.core.users.doctor import Doctor
from healthnet.core.users.nurse import Nurse
from healthnet.core.users.patient import Patient


class Command(BaseCommand):
    def handle(self, **options):
        exp = HealthNetExport()

        for h in Hospital.objects.all():
            exp.add_hospital(pk=h.pk, name=h.name, addr=h.get_address_str())

        for i in Administrator.objects.all():
            exp.add_admin(pk=i.pk, username=i.username, password_hash=i.password, first_name=i.first_name,
                          last_name=i.last_name, middle_name="", dob=datetime.datetime.now(), addr="", email="",
                          phone="",
                          primary_hospital_id=i.hospitals.pk, hospital_ids=[i.hospitals.pk])

        for i in Doctor.objects.all():
            exp.add_doctor(pk=i.pk, username=i.username, password_hash=i.password, first_name=i.first_name,
                           last_name=i.last_name, middle_name="", dob=datetime.datetime.now(), addr="", email="",
                           phone="",
                           hospital_ids=[h.pk for h in i.get_hospitals()], patient_ids=[p.pk for p in i.get_patients()])

        for i in Nurse.objects.all():
            exp.add_nurse(pk=i.pk, username=i.username, password_hash=i.password, first_name=i.first_name,
                          last_name=i.last_name, middle_name="", dob=datetime.datetime.now(), addr="", email="",
                          phone="",
                          primary_hospital_id=i.get_hospitals()[0].pk if len(i.get_hospitals()) > 0 else None,
                          doctor_ids=[d.pk for d in i.doctors.all()])

        for i in Patient.objects.all():
            exp.add_patient(pk=i.pk, username=i.username, password_hash=i.password, first_name=i.first_name,
                            middle_name="", last_name=i.last_name, dob=i.dob, addr=i.get_address_str(), email="",
                            phone="", emergency_contact="", eye_color="", bloodtype="", height=i.height,
                            weight=i.weight, primary_hospital_id=i.hospital.pk if i.hospital is not None else None,
                            primary_doctor_id=i.primary_care_provider.pk if i.primary_care_provider is not None else None,
                            doctor_ids=[d.pk for d in i.doctors.all()] if len(i.doctors.all()) > 0 else [])

        print(exp.export_json())
