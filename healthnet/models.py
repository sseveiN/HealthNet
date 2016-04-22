from django.db import models

from healthnet.core.enumfield import EnumField

States = EnumField("Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware",
                   "District of Columbia", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
                   "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
                   "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey",
                   "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
                   "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah",
                   "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming")

# Import External Models
from healthnet.core.hospital import Hospital
from healthnet.core.users.user import User
from healthnet.core.users.patient import Patient
from healthnet.core.users.doctor import Doctor
from healthnet.core.users.nurse import Nurse
from healthnet.core.users.administrator import Administrator
from healthnet.core.logging import LogEntry
from healthnet.core.calendar import Calendar, Appointment
from healthnet.core.prescription import Prescription
from healthnet.core.result import Result


class MedicalRecord(models.Model):
    """
    MedicalRecord Model
    """
    pass
