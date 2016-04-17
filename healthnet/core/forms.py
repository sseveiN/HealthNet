from datetime import datetime
from django import forms
from django.contrib.admin import widgets
from django.forms import SelectDateWidget

from healthnet.core.messages import MessageType
from healthnet.core.users.patient import Patient
from healthnet.core.users.user import User
from healthnet.models import Appointment, Hospital, States
from django.http import request
from healthnet.core.users.doctor import Doctor


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
    # TODO: limit age, height, weight, cholesterol
    # TODO: lengthen health insurance provider
    # TODO: make address line 2 optional

    password = forms.CharField(widget=forms.PasswordInput)
    dob = forms.DateField(widget=SelectDateWidget(years=range(datetime.now().year, datetime.now().year - 110, -1)))

    class Meta:
        """
        Meta class
        """
        model = Patient

        fields = ['health_insurance_number', 'username', 'password', 'first_name', 'last_name', 'dob', 'sex',
                  'address_line_1', 'address_line_2', 'city', 'state', 'zipcode', 'home_phone', 'work_phone',
                  'marital_status', 'health_insurance_provider', 'primary_care_provider', 'doctors', 'height', 'weight',
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
        self.fields['height'].required = False
        self.fields['weight'].required = False
        self.fields['cholesterol'].required = False
        self.fields['dob'].required = False
        self.fields['address_line_1'].required = False
        self.fields['address_line_2'].required = False
        self.fields['city'].required = False
        self.fields['state'].required = False
        self.fields['zipcode'].required = False
        self.fields['home_phone'].required = False
        self.fields['work_phone'].required = False
        self.fields['sex'].required = False
        self.fields['marital_status'].required = False
        self.fields['health_insurance_provider'].required = False
        self.fields['doctors'].required = False
        self.fields['primary_care_provider'].required = False

        self.fields['dob'].label = "Date of Birth"


class EditPatientInfoForm(forms.ModelForm):
    """
    Form to edit patient info
    """

    class Meta:
        """
        Metaclass
        """
        model = Patient
        fields = ['health_insurance_number', 'home_phone', 'work_phone', 'marital_status',
                  'address_line_1', 'address_line_2', 'city', 'state', 'zipcode', 'health_insurance_provider',
                  'primary_care_provider', 'doctors', 'height', 'weight', 'cholesterol']
        exclude = ['username', 'password', 'first_name', 'last_name', 'dob', 'sex', 'age', 'prescriptions',
                   'appointments', 'is_admin', 'is_doctor', 'is_patient', 'is_nurse', 'last_login', 'records']

    def __init__(self, *args, **kwargs):
        """
        Initialize the form
        :param args: initial arguments
        :param kwargs: initial kwarguments
        """
        super(EditPatientInfoForm, self).__init__(*args, **kwargs)
        self.fields['height'].required = False
        self.fields['weight'].required = False
        self.fields['cholesterol'].required = False
        self.fields['address_line_1'].required = False
        self.fields['address_line_2'].required = False
        self.fields['city'].required = False
        self.fields['state'].required = False
        self.fields['zipcode'].required = False
        self.fields['home_phone'].required = False
        self.fields['work_phone'].required = False
        self.fields['marital_status'].required = False
        self.fields['health_insurance_provider'].required = False
        self.fields['doctors'].required = False
        self.fields['primary_care_provider'].required = False


class AppointmentForm(forms.ModelForm):
    """
    Form to create an appointment
    """
    # TODO: should only be able to select from own doctors
    attendees = forms.ModelMultipleChoiceField(queryset=User.objects.all())
    description = forms.CharField(widget=forms.Textarea)

    class Meta:
        """
        Metaclass
        """
        model = Appointment
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        """
        Initialize the form
        :param args: initial arguments
        :param kwargs: initial kwarguments
        """
        super(AppointmentForm, self).__init__(*args, **kwargs)
        self.fields['tstart'].label = "Start date/time"
        self.fields['tend'].label = "End date/time"
        self.fields['tstart'].help_text = "Format Example: 10/25/06 11:30"
        self.fields['tend'].help_text = "Format Example: 10/25/06 14:30"

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
    Form to send a message
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
    Form to send a message
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
