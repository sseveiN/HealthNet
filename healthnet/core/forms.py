from datetime import datetime

from django import forms
from django.forms import SelectDateWidget
from django.http import request

from healthnet.core.enumfield import EnumField
from healthnet.core.messages import MessageType
from healthnet.core.users.administrator import Administrator
from healthnet.core.users.doctor import Doctor
from healthnet.core.users.nurse import Nurse
from healthnet.core.users.patient import Patient
from healthnet.core.users.user import User
from healthnet.models import Appointment, Result, Prescription


class LoginForm(forms.Form):
    """
    Form to login
    """
    username = forms.CharField(label="Username", max_length=25)
    password = forms.CharField(widget=forms.PasswordInput())


class RegistrationForm(forms.ModelForm):
    """
    Form for registration
    """
    password = forms.CharField(widget=forms.PasswordInput)
    dob = forms.DateField(widget=SelectDateWidget(years=range(datetime.now().year, datetime.now().year - 110, -1)))

    class Meta:
        """
        Meta class
        """
        model = Patient

        fields = ['health_insurance_number', 'health_insurance_provider', 'username', 'password', 'first_name', 'last_name', 'dob', 'sex',
                  'address_line_1', 'address_line_2', 'city', 'state', 'zipcode', 'home_phone', 'work_phone',
                  'marital_status', 'primary_care_provider', 'doctors', 'hospital', 'height', 'weight',
                  'cholesterol']
        exclude = ['prescriptions', 'appointments', 'is_admin', 'is_doctor', 'is_patient', 'is_nurse', 'last_login',
                   'records']

    def __init__(self, *args, **kwargs):
        """
        Initialize the form
        :param args: initial arguments
        :param kwargs: initial kwarguments
        """
        super(RegistrationForm, self).__init__(*args, **kwargs)

        self.fields['height'].label = 'Height (in)'
        self.fields['weight'].label = 'Weight (lb)'
        self.fields['cholesterol'].label = 'Weight (mg/dL)'
        self.fields['dob'].label = "Date of Birth"


class EditPatientInfoForm(forms.ModelForm):
    """
    Form to edit patient info
    """
    class Meta:
        """
        Meta class
        """
        model = Patient
        fields = ['health_insurance_number', 'home_phone', 'work_phone', 'marital_status',
                  'address_line_1', 'address_line_2', 'city', 'state', 'zipcode', 'health_insurance_provider',
                  'primary_care_provider', 'doctors', 'hospital', 'height', 'weight', 'cholesterol']
        exclude = ['username', 'password', 'first_name', 'last_name', 'dob', 'sex', 'age', 'prescriptions',
                   'appointments', 'is_admin', 'is_doctor', 'is_patient', 'is_nurse', 'last_login', 'records']

    def __init__(self, *args, **kwargs):
        """
        Initialize the form
        :param args: initial arguments
        :param kwargs: initial kwarguments
        """
        super(EditPatientInfoForm, self).__init__(*args, **kwargs)

        self.fields['height'].label = 'Height (in)'
        self.fields['weight'].label = 'Weight (lb)'
        self.fields['cholesterol'].label = 'Weight (mg/dL)'


class AppointmentForm(forms.ModelForm):
    """
    Form to create an appointment
    """
    attendees = forms.ModelMultipleChoiceField(queryset=None)
    description = forms.CharField(widget=forms.Textarea)

    class Meta:
        """
        Meta class
        """
        model = Appointment
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        """
        Initialize the form
        :param args: initial arguments
        :param kwargs: initial kwarguments
        """
        self.creator = kwargs.pop('creator')

        super(AppointmentForm, self).__init__(*args, **kwargs)

        self.fields['tstart'].label = "Start date/time"
        self.fields['tend'].label = "End date/time"
        self.fields['tstart'].help_text = "Format Example: 10/25/06 11:30"
        self.fields['tend'].help_text = "Format Example: 10/25/06 14:30"

        self.fields['attendees'].queryset = User.objects.exclude(pk=self.creator.pk)

    @staticmethod
    def edit_appointment(pk):
        """
        Edit the appointment
        :param pk: pk of the appointment
        :return: the appointment form
        """
        appointment = Appointment.objects.get(pk)
        appointment_form = AppointmentForm(request.POST, instance=appointment)
        appointment_form.save()
        return appointment_form


class ResultForm(forms.ModelForm):
    """
    The form to create a result
    """
    test_date = forms.DateField(widget=forms.SelectDateWidget, initial=datetime.now())
    description = forms.CharField(widget=forms.Textarea)

    class Meta:
        """
        Meta class
        """
        model = Result
        fields = '__all__'
        exclude = ['patient', 'doctor', 'is_released', 'release_date']

    def __init__(self, *args, **kwargs):
        """
        Initialize the form
        :param args: initial arguments
        :param kwargs: initial kwarguments
        """
        super(ResultForm, self).__init__(*args, **kwargs)


class PrescriptionForm(forms.ModelForm):
    """
    The form to create a prescription
    """
    expiration_date = forms.DateField(widget=forms.SelectDateWidget, initial=datetime.now())
    description = forms.CharField(widget=forms.Textarea)
    zipcode = forms.IntegerField(widget=forms.NumberInput)
    refills = forms.IntegerField(widget=forms.NumberInput, min_value=0)
    # TODO: add form validation

    class Meta:
        """
        Meta class
        """
        model = Prescription
        fields = '__all__'
        exclude = ['patient', 'doctor']

    def __init__(self, *args, **kwargs):
        """
        Initialize the form
        :param args: initial arguments
        :param kwargs: initial kwarguments
        """
        super(PrescriptionForm, self).__init__(*args, **kwargs)
        self.fields['refills'].label = "Number of Refills"
        self.fields['expiration_date'].label = "Expiration Date"
        self.fields['name'].label = "Prescription/Medicine Name"
        self.fields['description'].label = "Instructions/Directions"


class SendMessageForm(forms.Form):
    """
    Form to send a message
    """
    recipient = forms.ModelChoiceField(queryset=None)
    type = forms.ChoiceField(choices=MessageType.get_choices())
    message = forms.CharField(widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        """
        Initialize the form
        :param args: initial arguments
        :param kwargs: initial kwarguments
        """
        self.sender = kwargs.pop('sender')

        super(SendMessageForm, self).__init__(*args, **kwargs)

        self.fields['recipient'].label = "Recipient"
        self.fields['type'].label = "Message Type"
        self.fields['message'].label = "Your Message"

        self.fields['recipient'].queryset = User.objects.exclude(pk=self.sender.pk)


class ReplyMessageForm(forms.Form):
    """
    Form to reply to a message
    """
    message = forms.CharField(widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        """
        Initialize the form
        :param args: initial arguments
        :param kwargs: initial kwarguments
        """
        super(ReplyMessageForm, self).__init__(*args, **kwargs)
        self.fields['message'].label = "Your Message"


class TransferForm(forms.Form):
    """
    Form to transfer a patient
    """
    transfer_to = forms.ModelChoiceField(queryset=None)

    def __init__(self, *args, **kwargs):
        """
        Initialize the form
        :param args: initial arguments
        :param kwargs: initial kwarguments
        """
        self.transferer = kwargs.pop('transferer')

        super(TransferForm, self).__init__(*args, **kwargs)

        self.fields['transfer_to'].label = ""
        self.fields['transfer_to'].queryset = self.transferer.get_hospitals()


class DoctorRegistrationForm(forms.ModelForm):
    """
    Form to register a doctor
    """
    password = forms.CharField(widget=forms.PasswordInput())
    hospitals = forms.MultipleChoiceField(widget=forms.MultipleChoiceField())

    class Meta:
        """
        Meta class
        """
        model = Doctor
        fields = ['username', 'password', 'first_name', 'last_name', 'hospitals']
        exclude = ['is_doctor', 'is_pending', 'last_login', 'is_admin', 'is_patient', 'is_nurse', 'appointments']

        def __init__(self, *args, **kwargs):
            """
            Initialize the form
            :param args:
            :param kwargs:
            """
            super(DoctorRegistrationForm, self).__init__(*args, **kwargs)





class EditDoctorInfoForm(forms.ModelForm):

    class Meta:
        """
        Metaclass
        """
        model = Doctor
        fields = ['first_name', 'last_name', 'hospitals']
        exclude = ['username', 'password', 'is_doctor', 'is_pending', 'last_login', 'is_admin', 'is_patient', 'is_nurse', 'appointments']

        def __init__(self, *args, **kwargs):
            """
            Initialize the form
            :param args:
            :param kwargs:
            """

            super(EditDoctorInfoForm, self).__init__(*args, **kwargs)


class NurseRegistrationForm(forms.ModelForm):
    """
    Form to register a nurse
    """
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        """
        Meta class
        """
        model = Nurse
        fields = ['username', 'password', 'first_name', 'last_name', 'hospital']
        exclude = ['is_doctor', 'is_pending', 'last_login', 'is_admin', 'is_patient', 'is_nurse', 'appointments']

        def __init__(self, *args, **kwargs):
            """
            Initialize the form
            :param args:
            :param kwargs:
            """
            super(NurseRegistrationForm, self).__init__(*args, **kwargs)


class EditNurseInfoForm(forms.ModelForm):

    class Meta:
        """
        Metaclass
        """
        model = Nurse
        fields = ['first_name', 'last_name', 'hospital']
        exclude = ['username', 'password', 'is_doctor', 'is_pending', 'last_login', 'is_admin', 'is_patient', 'is_nurse', 'appointments']

        def __init__(self, *args, **kwargs):
            """
            Initialize the form
            :param args:
            :param kwargs:
            """
            super(EditNurseInfoForm, self).__init__(*args, **kwargs)

class AdminRegistrationForm(forms.ModelForm):
    """
    Form to register an admin
    """
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        """
        Meta class
        """
        model = Administrator
        fields = ['username', 'password', 'first_name', 'last_name']
        exclude = ['is_doctor', 'is_pending', 'last_login', 'is_admin', 'is_patient', 'is_nurse', 'appointments', 'hospital']

        def __init__(self, *args, **kwargs):
            """
            Initialize the form
            :param args:
            :param kwargs:
            """
            super(AdminRegistrationForm, self).__init__(*args, **kwargs)


RegisterSelectType = EnumField('Patient', 'Doctor', 'Nurse', 'Administrator')


class RegistrationSelectForm(forms.Form):
    """
    Form to select a registration type
    """
    type = forms.ChoiceField(choices=RegisterSelectType.get_choices())

    def __init__(self, *args, **kwargs):
        """
        Initialize the form
        :param args: initial arguments
        :param kwargs: initial kwarguments
        """
        super(RegistrationSelectForm, self).__init__(*args, **kwargs)

        self.fields['type'].label = "What are you?"
