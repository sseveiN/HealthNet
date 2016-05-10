import datetime

from django.core.management import BaseCommand

from healthnet.core.calendar import Appointment
from healthnet.core.healthnet_porter import HealthNetExport
from healthnet.core.hospital import Hospital
from healthnet.core.logging import LogEntry
from healthnet.core.prescription import Prescription
from healthnet.core.result import Result
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
                          last_name=i.last_name, middle_name="", dob=datetime.datetime.now(), addr="", email=i.email,
                          phone="",
                          primary_hospital_id=i.hospital.pk, hospital_ids=[i.hospital.pk])

        for i in Doctor.objects.all():
            exp.add_doctor(pk=i.pk, username=i.username, password_hash=i.password, first_name=i.first_name,
                           last_name=i.last_name, middle_name="", dob=datetime.datetime.now(), addr="", email=i.email,
                           phone="",
                           hospital_ids=[h.pk for h in i.get_hospitals()], patient_ids=[p.pk for p in i.get_patients()])

        for i in Nurse.objects.all():
            exp.add_nurse(pk=i.pk, username=i.username, password_hash=i.password, first_name=i.first_name,
                          last_name=i.last_name, middle_name="", dob=datetime.datetime.now(), addr="", email=i.email,
                          phone="",
                          primary_hospital_id=i.hospital.pk if i.hospital is not None else None,
                          doctor_ids=[])

        for i in Patient.objects.all():
            exp.add_patient(pk=i.pk, username=i.username, password_hash=i.password, first_name=i.first_name,
                            middle_name="", last_name=i.last_name, dob=i.dob, addr=i.get_address_str(), email=i.email,
                            phone=i.home_phone, emergency_contact=i.emergency_contact + ' ' + i.emergency_contact_number, eye_color="", bloodtype="", height=i.height,
                            weight=i.weight, primary_hospital_id=i.hospital.pk if i.hospital is not None else None,
                            primary_doctor_id=i.primary_care_provider.pk if i.primary_care_provider is not None else None,
                            doctor_ids=[i.primary_care_provider.pk] if i.primary_care_provider is not None else [])

        for i in Appointment.objects.all():
            exp.add_appointment(start=i.tstart, end=i.tend, location="", description=i.description,
                                doctor_ids=[u.pk for u in i.attendees.filter(is_doctor=True)],
                                patient_ids=[u.pk for u in i.attendees.filter(is_patient=True)],
                                nurse_ids=[u.pk for u in i.attendees.filter(is_nurse=True)])

        for i in Prescription.objects.all():
            exp.add_prescription(name=i.name, dosage=i.refills,
                                 notes="Expires: " + str(i.expiration_date) + "\n" + i.description,
                                 doctor_id=i.doctor.pk, patient_id=i.patient.pk)

        for i in Result.objects.all():
            exp.add_test(name=i.description, description=i.description, date=i.test_date, released=i.is_released,
                         results=i.comment, doctor_id=i.doctor.pk, patient_id=i.patient.pk)

        for i in LogEntry.objects.all():
            exp.add_log_entry(user_id=None, request_method="", request_secure=False, request_addr="",
                              description=str(i.datetime) + " [" + i.get_level_str() + "] " + i.message,
                              hospital_id=None)

        print(exp.export_json(), end="")
