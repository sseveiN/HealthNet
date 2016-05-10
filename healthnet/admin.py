from django.contrib import admin

from healthnet import models
from healthnet.core.logging import LogEntry
from healthnet.core.messages import Message
from healthnet.core.users.administrator import Administrator
from healthnet.core.users.doctor import Doctor
from healthnet.core.users.nurse import Nurse
from healthnet.core.users.patient import Patient
from healthnet.core.users.user import User

admin.site.register(models.Hospital)
admin.site.register(LogEntry)
admin.site.register(models.Appointment)
admin.site.register(models.Calendar)
admin.site.register(models.Prescription)
admin.site.register(Administrator)
admin.site.register(User)
admin.site.register(Patient)
admin.site.register(Doctor)
admin.site.register(Nurse)
admin.site.register(models.Result)

admin.site.register(Message)
