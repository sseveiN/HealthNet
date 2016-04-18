from django.contrib import admin

from healthnet import models
from healthnet.core.logging import LogEntry
from healthnet.core.users.user import User
from healthnet.core.users.patient import Patient
from healthnet.core.users.doctor import Doctor
from healthnet.core.users.nurse import Nurse

admin.site.register(models.Hospital)
admin.site.register(LogEntry)
admin.site.register(models.Address)
admin.site.register(models.Appointment)
admin.site.register(models.Calendar)
admin.site.register(models.Prescription)
admin.site.register(models.MedicalRecord)
admin.site.register(User)
admin.site.register(Patient)
admin.site.register(Doctor)
admin.site.register(Nurse)
admin.site.register(models.Result)