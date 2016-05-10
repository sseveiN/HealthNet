import django
from django import forms
from django.core.validators import RegexValidator
from django.forms import SelectDateWidget
from django.http import request

from healthnet.core.enumfield import EnumField
from healthnet.core.messages import MessageType
from healthnet.core.users.administrator import Administrator
from healthnet.core.users.doctor import Doctor
from healthnet.core.users.nurse import Nurse
from healthnet.core.users.patient import Patient
from healthnet.core.users.user import User
from healthnet.models import Appointment, Result, Prescription, Hospital, States


class LoginForm(forms.Form):
    """
    Form to login
    """
    username = forms.CharField(label="Username", max_length=25)
    password = forms.CharField(widget=forms.PasswordInput())


class RequiredRegistrationForm(forms.Form):
    """
    Form for required information of the patient
    """

    health_id = forms.CharField(label="Health Insurance Number", max_length=12,
                                validators=[RegexValidator(regex='^[a-zA-z]{1}[a-zA-z0-9]{11}$',
                                                           message='Health insurance alphanumeric beginning with a letter.')])
    email = forms.EmailField(label="Email")
    username = forms.CharField(max_length=25, label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())
    first_name = forms.CharField(max_length=50, label="First Name")
    last_name = forms.CharField(max_length=50, label="Last Name")
    dob = forms.DateField(label="Date Of Birth", widget=SelectDateWidget(
            years=range(django.utils.timezone.now().year, django.utils.timezone.now().year - 110, -1)))
    hospital = forms.ModelChoiceField(label="Hospital", queryset=Hospital.objects.all(), empty_label=None)


class RegistrationForm(forms.Form):
    Gender = EnumField('Male', 'Female', 'Unspecified')
    MaritalStatus = EnumField('Married', 'Living Common Law', 'Widowed', 'Separated', 'Divorced', 'Single',
                              'Unspecified')

    pcp = forms.ModelChoiceField(label="Primary Care Provider", queryset=Doctor.objects.none(), empty_label=None)

    health_insurance_provider = forms.CharField(label="Health Insurance Provider", max_length=30, required=False)
    home_phone = forms.CharField(label="Home Phone Number", max_length=12, required=False)
    work_phone = forms.CharField(label="Work Phone Number", max_length=12, required=False)
    sex = forms.ChoiceField(label="Sex", choices=Gender.get_choices(), required=False)
    marital_status = forms.ChoiceField(label="Marital Status", choices=MaritalStatus.get_choices(), required=False)
    address_line_1 = forms.CharField(label="Address Line 1", max_length=255, required=False)
    address_line_2 = forms.CharField(label="Address Line 2", max_length=255, required=False)
    city = forms.CharField(label="City", max_length=255, required=False)
    state = forms.ChoiceField(label="State", choices=States.get_choices(), required=False)
    zipcode = forms.CharField(label="Zipcode", max_length=5, required=False)
    next_of_kin = forms.CharField(label="Next Of Kin", max_length=255, required=False)
    emergency_contact = forms.CharField(label="Emergency Contact", max_length=255, required=False)
    emergency_contact_number = forms.CharField(label="Emergency Contact Number", max_length=12, required=False)
    height = forms.IntegerField(label="Height (in)", max_value=96, min_value=0, required=False)
    weight = forms.IntegerField(label="Weight (lbs)", max_value=400, min_value=0, required=False)
    cholesterol = forms.IntegerField(label="Cholesterol (mg/dL)", max_value=300, min_value=0, required=False)

    def __init__(self, *args, **kwargs):
        qs = kwargs.pop('qs', Doctor.objects.all())
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['pcp'].queryset = qs


class EditPatientInfoForm(forms.ModelForm):
    primary_care_provider = forms.ModelChoiceField(queryset=Doctor.get_approved().all())

    """
    Form to edit patient info
    """

    class Meta:
        """
        Meta class
        """
        model = Patient
        fields = ['health_insurance_number', 'email', 'home_phone', 'work_phone', 'marital_status',
                  'address_line_1', 'address_line_2', 'city', 'state', 'zipcode', 'health_insurance_provider',
                  'primary_care_provider', 'hospital', 'height', 'weight', 'cholesterol']
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
    attendees = forms.ModelMultipleChoiceField(queryset=None, widget=forms.CheckboxSelectMultiple)
    description = forms.CharField(widget=forms.Textarea)

    class Meta:
        """
        Meta class
        """
        model = Appointment
        fields = '__all__'
        exclude = ['creator']

    def __init__(self, *args, **kwargs):
        """
        Initialize the form
        :param args: initial arguments
        :param kwargs: initial kwarguments
        """
        self.attendees = kwargs.pop('attendees')
        self.is_doctor = kwargs.pop('is_doctor')

        super(AppointmentForm, self).__init__(*args, **kwargs)

        self.fields['tstart'].label = "Start date/time"
        self.fields['tend'].label = "End date/time"
        self.fields['tstart'].help_text = "Format Example: 10/25/06 11:30"
        self.fields['tend'].help_text = "Format Example: 10/25/06 14:30"

        self.fields['attendees'].queryset = self.attendees

        if not self.is_doctor:
            self.fields['tstart'].widget = forms.HiddenInput()
            self.fields['tend'].widget = forms.HiddenInput()

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
    The form to create a test result
    """
    test_date = forms.DateField(widget=forms.SelectDateWidget, initial=django.utils.timezone.now())
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
        self.fields['file'].label = "Test Files"


class PrescriptionForm(forms.ModelForm):
    """
    The form to create a prescription
    """
    expiration_date = forms.DateField(widget=forms.SelectDateWidget, initial=django.utils.timezone.now())

    issue_date = forms.DateField(widget=SelectDateWidget(
            years=range(django.utils.timezone.now().year, django.utils.timezone.now().year - 110, -1)),
            initial=django.utils.timezone.now())

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
    transfer_to = forms.ModelChoiceField(queryset=Hospital.objects.all())

    def __init__(self, *args, **kwargs):
        """
        Initialize the form
        :param args: initial arguments
        :param kwargs: initial kwarguments
        """
        self.transferer = kwargs.pop('transferer')

        super(TransferForm, self).__init__(*args, **kwargs)

        self.fields['transfer_to'].label = ""
        self.fields['transfer_to'].queryset = Hospital.objects.all()


class DoctorRegistrationForm(forms.ModelForm):
    """
    Form to register a doctor
    """

    hospitals = forms.ModelMultipleChoiceField(queryset=Hospital.objects.all().order_by('name'),
                                               widget=forms.CheckboxSelectMultiple)
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        """
        Meta class
        """
        model = Doctor
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'hospitals']
        exclude = ['is_doctor', 'is_pending', 'last_login', 'is_admin', 'is_patient', 'is_nurse', 'appointments']

        def __init__(self, *args, **kwargs):
            """
            Initialize the form
            :param args:
            :param kwargs:
            """
            super(DoctorRegistrationForm, self).__init__(*args, **kwargs)


class EditDoctorInfoForm(forms.ModelForm):
    hospitals = forms.ModelMultipleChoiceField(queryset=Hospital.objects.all().order_by('name'),
                                               widget=forms.CheckboxSelectMultiple)

    m2m_hospital = 'hospitals'
    m2m_hospitals = []
    m2m_nurses = []

    class Meta:
        """
        Metaclass
        """
        model = Doctor
        fields = ['email', 'first_name', 'last_name', 'hospitals']
        exclude = ['username', 'password', 'is_doctor', 'is_pending', 'last_login', 'is_admin', 'is_patient',
                   'is_nurse', 'appointments']

    def save(self, commit=True):
        """
        Saving m2m
        """
        instance = super(EditDoctorInfoForm, self).save(commit=True)
        if self.m2m_hospital:
            self.m2m_hospitals = [self.m2m_hospital]

        for field in self.m2m_hospitals:
            m2mfield = getattr(instance, field)
            for obj in self.cleaned_data.get(field):
                m2mfield.add(obj)

        if commit:
            instance.save()

        return instance


class NurseRegistrationForm(forms.ModelForm):
    """
    Form to register a nurse
    """
    password = forms.CharField(widget=forms.PasswordInput())
    hospital = forms.ModelChoiceField(queryset=Hospital.objects.all().order_by('name'))

    class Meta:
        """
        Meta class
        """
        model = Nurse
        fields = ['email', 'username', 'password', 'first_name', 'last_name', 'hospital']
        exclude = ['is_doctor', 'is_pending', 'last_login', 'is_admin', 'is_patient', 'is_nurse', 'appointments']

        def __init__(self, *args, **kwargs):
            """
            Initialize the form
            :param args:
            :param kwargs:
            """
            super(NurseRegistrationForm, self).__init__(*args, **kwargs)


class EditNurseInfoForm(forms.ModelForm):
    hospital = forms.ModelChoiceField(queryset=Hospital.objects.all().order_by('name'))

    class Meta:
        """
        Metaclass
        """
        model = Nurse
        fields = ['email', 'first_name', 'last_name', 'hospital']
        exclude = ['username', 'password', 'is_doctor', 'is_pending', 'last_login', 'is_admin', 'is_patient',
                   'is_nurse', 'appointments']

        def __init__(self, *args, **kwargs):
            """
            Initialize the form
            :param args:
            :param kwargs:
            """
            super(EditNurseInfoForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        """
        Saving m2m
        """
        instance = super(EditNurseInfoForm, self).save(commit=True)

        if commit:
            instance.save()

        return instance


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
        fields = ['email', 'username', 'password', 'first_name', 'last_name']
        exclude = ['is_doctor', 'is_pending', 'last_login', 'is_admin', 'is_patient', 'is_nurse', 'appointments',
                   'hospital']

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


class AppointmentOne(forms.Form):
    attendees = forms.ModelMultipleChoiceField(queryset=None, widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        """
        Initialize the form
        :param args: initial arguments
        :param kwargs: initial kwarguments
        """
        self.attendees = kwargs.pop('attendees')

        super(AppointmentOne, self).__init__(*args, **kwargs)

        self.fields['attendees'].label = "Who is attending this appointment?"
        self.fields['attendees'].queryset = self.attendees


class AppointmentTwo(forms.Form):
    time = forms.DateTimeField(input_formats=['%Y-%m-%dT%H:%M:%S'], widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        """
        Initialize the form
        :param args: initial arguments
        :param kwargs: initial kwarguments
        """
        super(AppointmentTwo, self).__init__(*args, **kwargs)


class AppointmentThree(forms.ModelForm):
    """
    Form to create an appointment
    """
    description = forms.CharField(widget=forms.Textarea)

    class Meta:
        """
        Meta class
        """
        model = Appointment
        fields = '__all__'
        exclude = ['creator', 'tend', 'tstart', 'attendees']

    def __init__(self, *args, **kwargs):
        """
        Initialize the form
        :param args: initial arguments
        :param kwargs: initial kwarguments
        """

        super(AppointmentThree, self).__init__(*args, **kwargs)

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
