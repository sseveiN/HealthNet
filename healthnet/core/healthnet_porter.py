__author__ = "Dakota Baber"
__email__ = "dakota@mail.rit.edu"

import copy
import json

from datetime import date as date_type, datetime
from datetime import datetime as datetime_type

import dateutil


class HealthNetImport(object):
    # This will map an arbitrary index to a real pk
    __pk_map = {
        'hospitals': {},
        'admins': {},
        'doctors': {},
        'nurses': {},
        'patients': {},
    }

    data = None

    """
    Represents a function with the following args and types:
        String name
        String addr
    Example:
        def create_hospital(name, address):
            # create the hospital object
    """
    create_hospital = None

    """
    Represents a function with the following args and types:
        String username
        String password_hash
        String first_name
        String middle_name
        String last_name
        String dob
        String addr
        String email
        String phone
        int primary_hospital_id
        [int] hospital_ids
    """
    create_admin = None

    """
    Represents a function with the following args and types:
        String username
        String password_hash
        String first_name
        String middle_name
        String last_name
        String dob
        String addr
        String email
        String phone
        [int] hospital_ids
        [int] patient_ids
    """
    create_doctor = None

    """
    Represents a function with the following args and types:
        String username
        String password_hash
        String first_name
        String middle_name
        String last_name
        String dob
        String addr
        String email
        String phone
        int primary_hospital_id
        [int] doctor_ids
    And returns the pk of the created object
    """
    create_nurse = None

    """
    Represents a function with the following args and types:
        String username
        String password_hash
        String first_name
        String middle_name
        String last_name
        String dob
        String addr
        String email
        String phone
        String emergency_contact
        String eye_color
        String bloodtype
        int height
        int weight
        int primary_hospital_id
        int primary_doctor_id
        [int] doctor_ids
    And returns the pk of the created object
    """
    create_patient = None

    """
    Represents a function with the following args and types:
        String name
        int dosage
        String notes
        int doctor_id
        int patient_id
    """
    create_prescription = None

    """
    Represents a function with the following args and types:
        String name
        String date
        String description
        String results
        bool released
        int doctor_id
        int patient_id
    """
    create_test = None

    """
    Represents a function with the following args and types:
        String start_timestamp
        String end_timestamp
        String location
        String description
        [int] attendee_ids
    """
    create_appointment = None

    """
        Represents a function with the following args and types:
        int user_id
        String request_method
        bool request_secure
        String request_addr
        String description
        int hospital_id
    """
    create_log = None

    def __init__(self, json_data, create_hospital_func=None, create_admin_func=None, create_doctor_func=None,
                 create_nurse_func=None, create_patient_func=None, create_appointment_func=None,
                 create_prescription_func=None, create_test_func=None, create_log_func=None):
        self.data = json.loads(json_data)

        self.create_hospital = create_hospital_func
        self.create_admin = create_admin_func
        self.create_doctor = create_doctor_func
        self.create_nurse = create_nurse_func
        self.create_patient = create_patient_func
        self.create_appointment = create_appointment_func
        self.create_prescription = create_prescription_func
        self.create_test = create_test_func
        self.create_log = create_log_func

    @staticmethod
    def __parse_date(timestr):
        return datetime.strptime(timestr, "%Y-%m-%dT%H:%M:%S")

    def import_all(self):
        """
        Import all objects in the JSON file
        :return: None
        """
        self.import_hospitals()
        self.import_patients()
        self.import_admins()
        self.import_doctors()
        self.import_nurses()
        self.import_appointments()
        self.import_tests()
        self.import_prescriptions()
        self.import_log_entries()

    def import_hospitals(self):
        if self.create_hospital is None:
            return

        pk_map_index = 0
        for i in self.data['hospitals']:
            pk = self.create_hospital(name=i['name'], addr=i['addr'])
            self.__pk_map[pk_map_index] = pk
            pk_map_index += 1

    def import_admins(self):
        if self.create_admin is None:
            return

        pk_map_index = 0
        for i in self.data['admins']:
            pk = self.create_admin(username=i['username'], password_hash=i['password_hash'],
                                   first_name=i['first_name'], middle_name=i['middle_name'], last_name=i['last_name'],
                                   dob=self.__parse_date(i['dob']), addr=i['addr'], email=i['email'],
                                   phone=i['phone'], primary_hospital_id=i['primary_hospital_id'],
                                   hospital_ids=i['hospital_ids'])
            self.__pk_map[pk_map_index] = pk
            pk_map_index += 1

    def import_doctors(self):
        if self.create_doctor is None:
            return

        pk_map_index = 0
        for i in self.data['doctors']:
            pk = self.create_doctor(username=i['username'], password_hash=i['password_hash'],
                                    first_name=i['first_name'], middle_name=i['middle_name'], last_name=i['last_name'],
                                    dob=self.__parse_date(i['dob']), addr=i['addr'], email=i['email'],
                                    phone=i['phone'], hospital_ids=i['hospital_ids'],
                                    patient_ids=i['patient_ids'])
            self.__pk_map[pk_map_index] = pk
            pk_map_index += 1

    def import_nurses(self):
        if self.create_nurse is None:
            return

        pk_map_index = 0
        for i in self.data['doctors']:
            pk = self.create_nurse(username=i['username'], password_hash=i['password_hash'],
                                   first_name=i['first_name'], middle_name=i['middle_name'], last_name=i['last_name'],
                                   dob=self.__parse_date(i['dob']), addr=i['addr'], email=i['email'],
                                   phone=i['phone'], primary_hospital_id=i['primary_hospital_id'],
                                   doctor_ids=i['doctor_ids'])
            self.__pk_map[pk_map_index] = pk
            pk_map_index += 1

    def import_patients(self):
        if self.create_patient is None:
            return

        pk_map_index = 0
        for i in self.data['patients']:
            pk = self.create_patient(username=i['username'], password_hash=i['password_hash'],
                                     first_name=i['first_name'], middle_name=i['middle_name'], last_name=i['last_name'],
                                     dob=self.__parse_date(i['dob']), addr=i['addr'], email=i['email'],
                                     phone=i['phone'], emergency_contact=i['emergency_contact'],
                                     eye_color=i['eye_color'],
                                     bloodtype=i['bloodtype'], weight=i['weight'],
                                     primary_hospital_id=i['primary_hospital_id'],
                                     primary_doctor_id=i['primary_doctor_id'], doctor_ids=i['doctor_ids'])
            self.__pk_map[pk_map_index] = pk
            pk_map_index += 1

    def import_appointments(self):
        if self.create_appointment is None:
            return

        for i in self.data['appointments']:
            self.create_appointment(start=self.__parse_date(i['start']), end=self.__parse_date(i['end']),
                                    location=i['location'], description=i['description'],
                                    attendee_ids=i['attendee_ids'])

    def import_prescriptions(self):
        if self.create_prescription is None:
            return

        for i in self.data['appointments']:
            self.create_prescription(name=i['name'], dosage=i['dosage'], notes=i['notes'],
                                     doctor_id=i['doctor_id'], patient_id=i['patient_id'])

    def import_tests(self):
        if self.create_test is None:
            return

        for i in self.data['tests']:
            self.create_test(nmae=i['name'], date=self.__parse_date(i['date']), description=i['description'],
                             results=i['results'], released=i['released'], doctor_id=i['doctor_id'],
                             patient_id=i['patient_id'])

    def import_log_entries(self):
        if self.create_log is None:
            return

        for i in self.data['log_entries']:
            self.create_log(user_id=i['user_id'], request_method=i['request_method'],
                            request_secure=i['request_secure'],
                            request_addr=i['request_addr'], description=i['description'], hospital_id=i['hospital_id'])


class HealthNetExport(object):
    """
    Exports HealthNet data to be used by other implementations
    of HealthNet.
    """

    # This will map a real pk to an arbitrary index
    __pk_map = {
        'hospitals': {},
        'admins': {},
        'doctors': {},
        'nurses': {},
        'patients': {},
    }

    # The main scheme that will be exported to JSON
    __export_scheme = {
        'hospitals': [],
        'admins': [],
        'doctors': [],
        'nurses': [],
        'patients': [],
        'appointments': [],
        'tests': [],
        'prescriptions': [],
        'log_entries': [],
    }

    def add_hospital(self, pk, name: str, addr: str):
        """
        Add a hospital to be exported
        :param pk: The pk of this hospital
        :param name: The name of this hospital
        :param addr: The address of this hospital
        :return: None
        """
        self.__pk_map['hospitals'][pk] = len(self.__pk_map['hospitals'])
        self.__export_scheme['hospitals'] += [{
            'name': name,
            'addr': addr
        }]

    def add_admin(self, pk, username: str, password_hash: str, first_name: str, last_name: str, middle_name: str,
                  dob: date_type, addr: str, email: str, phone: str, primary_hospital_id: int, hospital_ids: list):
        """
        Add an admin to be exported
        :param pk: The pk of this admin
        :param username: The username of this admin
        :param password_hash: The password_hash of this admin
        :param first_name: The first_name of this admin
        :param last_name: The last name of this admin
        :param middle_name: The middle name of this admin
        :param dob: The date of birth for this admin
        :param addr: The address of this admin
        :param email: The email for this admin
        :param phone: The phone number for this admin
        :param primary_hospital_id: The id of the primary hospital for this admin
        :param hospital_ids: A list of ids for the hospitals associated with this admin
        :return: None
        """
        self.__pk_map['admins'][pk] = len(self.__pk_map['admins'])
        self.__export_scheme['admins'] += [{
            'username': username,
            'password_hash': password_hash,
            'first_name': first_name,
            'middle_name': middle_name,
            'last_name': last_name,
            'dob': dob.isoformat(),
            'addr': addr,
            'email': email,
            'phone': phone,
            'primary_hospital_id': primary_hospital_id,
            'hospital_ids': hospital_ids
        }]

    def add_doctor(self, pk, username: str, password_hash: str, first_name: str, last_name: str, middle_name: str,
                   dob: date_type, addr: str, email: str, phone: str, hospital_ids: list, patient_ids: list):
        """
        Add a doctor to be exported
        :param pk: The pk of this doctor
        :param username: The username of this doctor
        :param password_hash: The password hash of this doctor
        :param first_name: The first name of this doctor
        :param last_name: The last name of this doctor
        :param middle_name: The middle name of this doctor
        :param dob: The birth date of this doctor
        :param addr: The address of this doctor
        :param email: The email for this doctor
        :param phone: The phone number for this doctor
        :param hospital_ids: A list of hospital ids associated with this doctor
        :param patient_ids: A list of patient ids associated with this doctor
        :return: None
        """
        self.__pk_map['doctors'][pk] = len(self.__pk_map['doctors'])
        self.__export_scheme['doctors'] += [{
            'username': username,
            'password_hash': password_hash,
            'first_name': first_name,
            'middle_name': middle_name,
            'last_name': last_name,
            'dob': dob.isoformat(),
            'addr': addr,
            'email': email,
            'phone': phone,
            'hospital_ids': hospital_ids,
            'patient_ids': patient_ids
        }]

    def add_nurse(self, pk, username: str, password_hash: str, first_name: str, last_name: str, middle_name: str,
                  dob: date_type, addr: str, email: str, phone: str, primary_hospital_id: list, doctor_ids: list):
        """
        Add a nurse to be exported
        :param pk: The pk for this nurse
        :param username: The username of this nurse
        :param password_hash: The password hash for this nurse
        :param first_name: The first name of the nurse
        :param last_name: The last name of the nurse
        :param middle_name: The middle name of the nurse
        :param dob: The birth date of this nurse
        :param addr: The address of this nurse
        :param email: The email of this nurse
        :param phone: The phone number of this nurse
        :param primary_hospital_id: The id of the primary hospital assocaited with this nurse
        :param doctor_ids: A lost of doctors ids associated with this nurse
        :return: None
        """
        self.__pk_map['nurses'][pk] = len(self.__pk_map['nurses'])
        self.__export_scheme['nurses'] += [{
            'username': username,
            'password_hash': password_hash,
            'first_name': first_name,
            'middle_name': middle_name,
            'last_name': last_name,
            'dob': dob.isoformat(),
            'addr': addr,
            'email': email,
            'phone': phone,
            'primary_hospital_id': primary_hospital_id,
            'doctor_ids': doctor_ids
        }]

    def add_patient(self, pk, username: str, password_hash: str, first_name: str, middle_name: str, last_name: str,
                    dob: date_type, addr: str, email: str, phone: str, emergency_contact: str, eye_color: str,
                    bloodtype: str, height: int, weight: int, primary_hospital_id: int, primary_doctor_id: int,
                    doctor_ids: list):
        """
        Add a patient to be exported
        :param pk: The pk of the patient
        :param username: The username of the patient
        :param password_hash: The password hash for this patient
        :param first_name: The first name of the patient
        :param middle_name: The middle name of the patient
        :param last_name: The last name of the patient
        :param dob: The birth date of the patient
        :param addr: The address of the patient
        :param email: The email of the patient
        :param phone: The phone number of the patient
        :param emergency_contact: The emergency contact for the patient
        :param eye_color: The eye color of the patient
        :param bloodtype: The blood type of the patient
        :param height: The height of the patient (in)
        :param weight: The weight of the patient (lbs)
        :param primary_hospital_id: The id of the primary hospital for this patient
        :param primary_doctor_id: The id of the primary doctor for this patient
        :param doctor_ids: A list of doctor ids associated with this patient
        :return: None
        """
        self.__pk_map['patients'][pk] = len(self.__pk_map['patients'])
        self.__export_scheme['patients'] += [{
            'username': username,
            'password_hash': password_hash,
            'first_name': first_name,
            'middle_name': middle_name,
            'last_name': last_name,
            'dob': dob.isoformat(),
            'addr': addr,
            'email': email,
            'phone': phone,
            'emergency_contact': emergency_contact,
            'eye_color': eye_color,
            'bloodtype': bloodtype,
            'height': height,
            'weight': weight,
            'primary_hospital_id': primary_hospital_id,
            'primary_doctor_id': primary_doctor_id,
            'doctor_ids': doctor_ids
        }]

    def add_appointment(self, start: datetime_type, end: datetime_type, location: str, description: str,
                        attendee_ids: list):
        """
        Add an appointment to be exported
        :param start: The start date of the appointment
        :param end: The end date of the appointment
        :param location: The physical location of the appointment
        :param description: A description of the appointment
        :param attendee_ids: A list of ids of the attendees
        :return: None
        """
        self.__export_scheme['appointments'] += [{
            'start': start.isoformat(),
            'end': end.isoformat(),
            'location': location,
            'description': description,
            'attendee_ids': attendee_ids
        }]

    def add_prescriptions(self, name: str, dosage: int, notes: str, doctor_id: int, patient_id: int):
        """
        Add a prescription to be exported
        :param name: The name of the drug
        :param dosage: The dosage for the drug
        :param notes: Additional notes
        :param doctor_id: The id of the doctor associated with the prescription
        :param patient_id: The id of the patient associated with the prescription
        :return: None
        """
        self.__export_scheme['prescriptions'] += [{
            'name': name,
            'dosage': dosage,
            'notes': notes,
            'doctor_id': doctor_id,
            'patient_id': patient_id
        }]

    def add_test(self, name: str, date: date_type, description: str, results: str, released: bool, doctor_id: int,
                 patient_id: int):
        """
        Add a test to be exported
        :param name: The name of the test
        :param date: The date of the test
        :param description: A description of the test
        :param results: The results associated with the test
        :param released: Whether or not the test is released
        :param doctor_id: The id of the doctor associated with the test
        :param patient_id: The id of the patient associated with this test
        :return: None
        """
        self.__export_scheme['tests'] += [{
            'name': name,
            'date': date.isoformat(),
            'description': description,
            'results': results,
            'released': released,
            'doctor_id': doctor_id,
            'patient_id': patient_id
        }]

    def add_log_entry(self, user_id: int, request_method: str, request_secure: bool, request_addr: str,
                      description: str, hospital_id: int):
        """
        Add a log entry to be exported
        :param user_id: The id of the user who logged this
        :param request_method: The request method for the HTTP request
        :param request_secure: Whether or not the request was secure
        :param request_addr: The address this entry was logged from
        :param description: A description of this entry
        :param hospital_id: The ID of the hospital this log entry is referencing
        :return: None
        """
        self.__export_scheme['log_entries'] += [{
            'user_id': user_id,
            'request_method': request_method,
            'request_secure': request_secure,
            'request_addr': request_addr,
            'description': description,
            'hospital_id': hospital_id
        }]

    def export_json(self):
        """
        Export the added models to a JSON string
        :return: a JSON string representing the added data
        """
        # Go through each object type and link them to their new pk_map ids
        # this will error if a nonexistent link attempt is made
        output_schema = copy.deepcopy(self.__export_scheme)

        # Admin pk_map
        for i in range(len(output_schema['admins'])):
            self.set_pk_for_field(output_schema, 'admins', i, 'hospitals', 'primary_hospital_id')

            for j in range(len(output_schema['admins'][i]['hospital_ids'])):
                self.set_pk_for_field_with_idx(output_schema, 'admins', i, 'hospitals', 'hospital_ids', j)

        # Patient pk_map
        for i in range(len(output_schema['patients'])):
            self.set_pk_for_field(output_schema, 'patients', i, 'hospitals', 'primary_hospital_id')
            self.set_pk_for_field(output_schema, 'patients', i, 'doctors', 'primary_doctor_id')

            for j in range(len(output_schema['patients'][i]['doctor_ids'])):
                self.set_pk_for_field_with_idx(output_schema, 'patients', i, 'doctors', 'doctor_ids', j)

        # Doctor pk_map
        for i in range(len(output_schema['doctors'])):
            for j in range(len(output_schema['doctors'][i]['patient_ids'])):
                self.set_pk_for_field_with_idx(output_schema, 'doctors', i, 'patients', 'patient_ids', j)

            for j in range(len(output_schema['doctors'][i]['hospital_ids'])):
                self.set_pk_for_field_with_idx(output_schema, 'doctors', i, 'hospitals', 'hospital_ids', j)

        # Nurse pk_map
        for i in range(len(output_schema['nurses'])):
            self.set_pk_for_field(output_schema, 'nurses', i, 'hospitals', 'primary_hospital_id')

            for j in range(len(output_schema['nurses'][i]['doctor_ids'])):
                self.set_pk_for_field_with_idx(output_schema, 'nurses', i, 'doctors', 'doctor_ids', j)

        # Patient pk_map
        for i in range(len(output_schema['patients'])):
            self.set_pk_for_field(output_schema, 'patients', i, 'hospitals', 'primary_hospital_id')
            self.set_pk_for_field(output_schema, 'patients', i, 'doctors', 'primary_doctor_id')

            for j in range(len(output_schema['patients'][i]['doctor_ids'])):
                self.set_pk_for_field_with_idx(output_schema, 'patients', i, 'doctors', 'doctor_ids', j)

        # return the json string
        return json.dumps(output_schema)

    def set_pk_for_field_with_idx(self, schema_map, schema_key, schema_index, pk_key, key_to_replace, idx):
        if schema_map[schema_key][schema_index][key_to_replace][idx] is None:
            return

        try:
            schema_map[schema_key][schema_index][key_to_replace][idx] = self.__pk_map[pk_key][schema_map[schema_key][schema_index][key_to_replace][idx]]
        except:
            pass

    def set_pk_for_field(self, schema_map, schema_key, schema_index, pk_key, key_to_replace):
        if schema_map[schema_key][schema_index][key_to_replace] is None:
            return

        try:
            schema_map[schema_key][schema_index][key_to_replace] = self.__pk_map[pk_key][schema_map[schema_key][schema_index][key_to_replace]]
        except:
            pass