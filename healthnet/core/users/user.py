from datetime import datetime

from django.contrib.auth import authenticate
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import UserManager
from django.db import models
from django.shortcuts import render

from healthnet.core.enumfield import EnumField
from healthnet.core.logging import Logging


class UserType(EnumField):
    """
    Refers to the type of user
    """
    Administrator = 0
    Doctor = 1
    Nurse = 2
    Patient = 3

    @staticmethod
    def get_type_name(usertype):
        """
        Gets a sting representation of this user type
        :param usertype: The UserType to get a string for
        :return: The string representation
        """
        if usertype == UserType.Administrator:
            return 'Administrator'
        if usertype == UserType.Doctor:
            return 'Doctor'
        if usertype == UserType.Nurse:
            return 'Nurse'
        if usertype == UserType.Patient:
            return 'Patient'
        return "Unknown"


class User(AbstractBaseUser):
    """
    The user class inherited by other user types
    """
    username = models.CharField(max_length=25, null=False, unique=True)
    email = models.EmailField()
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    is_admin = models.BooleanField(default=False)
    is_doctor = models.BooleanField(default=False)
    is_patient = models.BooleanField(default=False)
    is_nurse = models.BooleanField(default=False)

    # This should ALWAYS be false, only to be compatible with django admin
    is_staff = models.BooleanField(default=False)

    is_pending = models.BooleanField(default=True)

    appointments = models.ManyToManyField('Appointment', blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'

    @staticmethod
    def create_user(username, password, usertype: UserType, email, first_name="", last_name="", print_stdout=True,
                    primary_care_provider_id=None, hospital_id=None, health_insurance_number=None):
        """
        Creates the user with the specified parameters
        :param print_stdout: should we log this to stdout?
        :param username: user's username
        :param password: user's password
        :param usertype: the type of user
        :param first_name: user's first name
        :param last_name: user's last name
        :return: a new user with the specified parameters
        """
        try:
            """Check that a user with that username does not exist"""
            user = User.objects.get(username=username)
            if user is not None:
                return False, "A user with that name already exists"
        except User.DoesNotExist:
            pass

        """Define specific user traits"""
        if usertype == UserType.Administrator:
            user = Administrator(username=username, first_name=first_name, last_name=last_name)
            user.is_admin = True
        elif usertype == UserType.Doctor:
            from healthnet.core.users.doctor import Doctor
            user = Doctor(username=username, first_name=first_name, last_name=last_name)
            user.is_doctor = True
        elif usertype == UserType.Nurse:
            user = Nurse(username=username, first_name=first_name, last_name=last_name)
            user.is_nurse = True
        elif usertype == UserType.Patient:
            from healthnet.core.users.patient import Patient
            user = Patient(username=username, first_name=first_name, last_name=last_name, hospital_id=hospital_id,
                           primary_care_provider_id=primary_care_provider_id,
                           health_insurance_number=health_insurance_number)
            user.is_patient = True
        else:
            user = User(username=username, first_name=first_name, last_name=last_name)

        user.email = email
        user.set_password(password)
        user.save()

        Logging.info("User '%s' created" % username, print_stdout=print_stdout)

        return True, user

    def is_type(self, usertype: UserType):
        """
        Check to see if the user is of a certain type
        :param usertype: the user type being checked
        :return: true if the user is of the usertype, false otherwise
        """
        return self.get_user_type() == usertype

    @staticmethod
    def login(request, username, password):
        """
        Logging into the user
        :param request: request being addressed
        :param username: given username
        :param password: given password
        :return: user logging into
        """
        user = authenticate(username=username, password=password)

        if user is None:
            return None

        user.last_login = datetime.now()
        user.save()

        request.session['current_user_pk'] = user.pk
        request.session['current_user_username'] = username
        request.session['current_user_is_admin'] = user.is_admin
        request.session['current_user_is_nurse'] = user.is_nurse
        request.session['current_user_is_doctor'] = user.is_doctor
        request.session['current_user_is_patient'] = user.is_patient
        request.session['current_user_display_name'] = user.get_display_name()
        return user

    @staticmethod
    def logout(request):
        """
        Logs out of a user
        :param request: request being addressed
        """
        if 'current_user_pk' in request.session:
            del request.session['current_user_pk']
        if 'current_user_username' in request.session:
            del request.session['current_user_username']
        if 'current_user_is_admin' in request.session:
            del request.session['current_user_is_admin']
        if 'current_user_is_nurse' in request.session:
            del request.session['current_user_is_nurse']
        if 'current_user_is_doctor' in request.session:
            del request.session['current_user_is_doctor']
        if 'current_user_is_patient' in request.session:
            del request.session['current_user_is_patient']
        if 'current_user_display_name' in request.session:
            del request.session['current_user_display_name']

    @staticmethod
    def get_logged_in(request):
        """
        Check to see if logged in
        :param request: request being addressed
        :return: true if logged in, false otherwise
        """
        try:
            if request.session['current_user_pk'] is None:
                return None
        except KeyError:
            return None

        return User.objects.get(pk=request.session['current_user_pk'])

    def get_display_name(self):
        """
        Gets the display name of the user
        :return: name depending on the circumstance
        """
        name = self.get_full_name()
        if not name:
            return self.get_short_name()
        return name

    def get_full_name(self):
        """
        Gets the user's full name
        :return: user's full name
        """
        return ('%s %s' % (self.first_name, self.last_name)).strip()

    def get_short_name(self):
        """
        Gets the user's short name
        :return: user's short name
        """
        return self.username

    def get_user_type(self):
        """
        Gets the user's type
        :return: user's type
        """
        if self.is_admin:
            return UserType.Administrator
        if self.is_doctor:
            return UserType.Doctor
        if self.is_nurse:
            return UserType.Nurse
        if self.is_patient:
            return UserType.Patient

    def get_user_type_name(self):
        """
        Get the string representation of this users type
        :return: The string representing the user type
        """
        return UserType.get_type_name(self.get_user_type())

    def get_num_new_msgs(self):
        """
        Get the number of new messages this user has
        :return: An integer representing the number of new messages
        """
        return self.received_messages.filter(is_read=False).count()

    def get_view_context(self):
        """
        Get the global view context for this user
        :return: A dictionary representing view context
        """
        return {
            'num_msgs': self.get_num_new_msgs()
        }

    def mark_messages_read(self):
        """
        Mark all the users messages read
        :return: None
        """
        for i in self.received_messages.filter(is_read=False):
            i.is_read = True
            i.save()

    def render_for_user(self, request, template, context):
        """
        Render a view with this users context
        :param request: the http request
        :param template: the template to render
        :param context: additional context to use
        :return: The rendered page
        """
        user_context = dict(context)
        user_context.update(self.get_view_context())

        if self.is_type(UserType.Administrator):
            if Administrator.objects.get(pk=self.pk).hospital is not None:
                user_context['admin_hospital'] = Administrator.objects.get(pk=self.pk).hospital.pk

        return render(request, template, user_context)

    def get_typed_user(self):
        """
        Gets a user casted to their specific UserType
        :return: The type casted user
        """
        if self.is_type(UserType.Patient):
            from healthnet.core.users.patient import Patient
            return Patient.objects.get(username=self.username)

        if self.is_type(UserType.Doctor):
            from healthnet.core.users.doctor import Doctor
            return Doctor.objects.get(username=self.username)

        if self.is_type(UserType.Nurse):
            from healthnet.core.users.nurse import Nurse
            return Nurse.objects.get(username=self.username)

        if self.is_type(UserType.Administrator):
            from healthnet.core.users.administrator import Administrator
            return Administrator.objects.get(username=self.username)

        return self

    def get_appointments(self):
        """
        Get all the appointments for this user
        :return: A queryset of appointments
        """
        return self.get_typed_user().get_appointments()

    def get_patients(self):
        """
        Get all the patients for this user
        :return: A queryset of patients
        """
        if self.is_type(UserType.Doctor) or self.is_type(UserType.Nurse) or self.is_type(UserType.Administrator):
            return self.get_typed_user().get_patients()
        from healthnet.core.users.patient import Patient
        return Patient.objects.filter(pk=None)

    def has_patient(self, patient):
        """
        Check if this user has access to a patient
        :param patient: The patient to check access for
        :return: Whether or not the user has access
        """
        if not patient.is_type(UserType.Patient):
            return False

        patient = patient.get_typed_user()

        if patient.primary_care_provider is None:
            return False

        if patient.primary_care_provider.pk == self.pk:
            return True

        from healthnet.core.users.patient import Patient
        if type(patient) == User or type(patient) == Patient:
            patient = patient.pk

        for p in self.get_patients():
            if patient == p.pk:
                return True
        return False

    def notify(self, msg):
        """
        Send a notification to this user
        :param msg: The message for the notification
        :return: None
        """
        from healthnet.core.messages import Message, MessageType
        msg = Message.send(self, self, msg, MessageType.Normal)
        msg.is_notification = True
        msg.save()

    def approve(self):
        """
        Approve a user
        :return: None
        """
        self.is_pending = False
        self.save()

    @staticmethod
    def generify_queryset(typed_user_set):
        """
        Casts a queryset of administrator, doctor, nurse or patient to
        a generic user queryset
        :param typed_user_set: A query set of non generic users
        :return: A query set of generic users
        """
        out = User.objects.filter(pk=None)
        for u in typed_user_set:
            out |= User.objects.filter(pk=u.pk)
        return out

    def __unicode__(self):
        """
        :return: The unicode representation of the object
        """
        return '%s (%s)' % (self.get_full_name(), self.get_short_name())

    def __str__(self):
        """
        :return: The string representation of the object
        """
        return self.__unicode__()


class UserBackend(object):
    """
    Backend to the user
    """

    def authenticate(self, username=None, password=None):
        """
        Authenticate the user
        :param username: user's username
        :param password: user's password
        :return: the user object
        """
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                Logging.info("Authenticated user '%s'" % username)
                return user
            else:
                return None
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        """
        Gets the user of the given id
        :param user_id: the user's id
        :return: the user
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


# Resolve cyclic dependencies
from healthnet.core.users.administrator import Administrator
from healthnet.core.users.nurse import Nurse
