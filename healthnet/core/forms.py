from django import forms
from django.contrib.admin import widgets

from healthnet.core.users.patient import Patient
from healthnet.models import Appointment
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
    # TODO: need to be able to add an address
    # TODO: limit age, height, weight, cholesterol
    # TODO: lengthen health insurance provider
    # TODO: choose multiple doctors
    # TODO:

    password = forms.CharField(widget=forms.PasswordInput)
    dob = forms.DateField(widget=forms.SelectDateWidget)

    address = forms.CharField()

    class Meta:
        """
        Meta class
        """
        model = Patient
        fields = ['health_insurance_number', 'username', 'password', 'first_name', 'last_name', 'dob', 'address', 'age', 'sex', 'home_phone', 'work_phone', 'marital_status', 'health_insurance_provider', 'primary_care_provider','doctors', 'height', 'weight', 'cholesterol']
        exclude = ['prescriptions', 'appointments', 'is_admin', 'is_doctor', 'is_patient', 'is_nurse', 'last_login', 'records', 'address']

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
        self.fields['address'].required = False
        self.fields['home_phone'].required = False
        self.fields['work_phone'].required = False
        self.fields['age'].required = False
        self.fields['sex'].required = False
        self.fields['marital_status'].required = False
        self.fields['health_insurance_provider'].required = False
        self.fields['doctors'].required = False
        self.fields['primary_care_provider'].required = False


class EditPatientInfoForm(forms.ModelForm):
    """
    Form to edit patient info
    """
    class Meta:
        """
        Metaclass
        """
        model = Patient
        fields = ['health_insurance_number', 'address', 'home_phone', 'work_phone', 'marital_status', 'health_insurance_provider', 'primary_care_provider','doctors', 'height', 'weight', 'cholesterol']
        exclude = ['username', 'password', 'first_name', 'last_name', 'dob', 'sex', 'age', 'prescriptions', 'appointments', 'is_admin', 'is_doctor', 'is_patient', 'is_nurse', 'last_login', 'records']

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
        self.fields['address'].required = False
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
    attendees = forms.ModelMultipleChoiceField(queryset=Doctor.objects.all())
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
