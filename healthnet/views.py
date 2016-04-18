from datetime import datetime

from django.contrib import messages
from django.contrib.auth import authenticate
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from healthnet.core.forms import LoginForm, RegistrationForm, AppointmentForm, EditPatientInfoForm, SendMessageForm, \
    ReplyMessageForm, TransferForm
from healthnet.core.logging import LogEntry
from healthnet.core.messages import Message, MessageType
from healthnet.core.users.administrator import Administrator
from healthnet.core.users.nurse import Nurse
from healthnet.core.users.user import User, UserType
from healthnet.core.users.patient import Patient
from healthnet.core.users.doctor import Doctor
from healthnet.models import Calendar, Appointment
from healthnet.core.logging import Logging


def index(request):
    """
    Logs a user in
    :param request: request to login
    :return: if Logged in already, go to dashboard
                Else, if valid login, go to dashboard
                Else, go to home page
    """
    user = User.get_logged_in(request)

    # Don't allow if logged in
    if user is not None:
        return redirect('dashboard')

    if request.method == 'POST':
        login_form = LoginForm(request.POST)

        if login_form.is_valid():
            user = User.login(request, request.POST['username'], request.POST['password'])

            if user is not None:
                if user.is_pending:
                    messages.error(request, "Your account is pending admin approval!")
                    User.logout(request)
                    return redirect('index')

                # creds valid; redirect to dashboard
                return redirect('dashboard')
            else:
                messages.error(request, "An incorrect username or password was provided!")
    else:
        login_form = LoginForm()

    context = {
        'login_form': login_form
    }

    return render(request, 'home.html', context)


def dashboard(request):
    """
    Creates the dashboard for a user
    :param request: request to go to the dashboard
    :return: render: A visualization of the dashboard for the user
    """
    user = User.get_logged_in(request)

    # Require login
    if user is None:
        return redirect('index')

    # Get list of appointments in json form
    appointments = Calendar.get_appointments_for_attendee_for_day(user, datetime.now())
    appointments_json = Calendar.get_appointments_json(user)

    pending = []
    if user.is_type(UserType.Administrator):
        pending = User.objects.filter(is_pending=True)

    context = {
        'appointments': appointments,
        'appointments_json': appointments_json,
        'username': request.user.username,
        'patients': user.get_patients(),
        'pending_users': pending
    }

    return user.render_for_user(request, 'dashboard.html', context)


def appointment(request):
    """
    User tries to create an appointment
    :param request: request to create an appointment
    :return: If the appointment is created, the dashboard, otherwise
                they stay on the appointment form with a message saying
                what they need to fix
    """
    user = User.get_logged_in(request)
    primary_key = user.pk

    if request.method == 'POST':
        appointment_form = AppointmentForm(request.POST)

        if appointment_form.is_valid():
            name = appointment_form.cleaned_data['name']
            description = appointment_form.cleaned_data['description']
            tstart = appointment_form.cleaned_data['tstart']
            tend = appointment_form.cleaned_data['tend']
            attendees = appointment_form.cleaned_data['attendees']

            appointment_form = AppointmentForm(request.POST)
            new_apt = appointment_form.save()
            me = User.objects.get(pk=primary_key)
            new_apt.attendees.add(me)

            if new_apt.has_conflict():
                messages.error(request, "There is a conflict with the selected times!")
                appointment_form = AppointmentForm(request.POST)
                new_apt.delete()
            else:
                new_apt.save()
                Logging.info("Created appointment '%s'" % name)
                return HttpResponseRedirect('/dashboard')
        else:
            print('invalid')
    else:
        appointment_form = AppointmentForm(request.POST)

    context = {
        'appointment_form': appointment_form
    }
    return user.render_for_user(request, 'appointment.html', context)


def registration(request):
    """
    User tries to register for account
    :param request: request to register for an account
    :return: If successful, user taken to dashboard, else, they are instructed
                to register again, with a message saying what they need to fix
    """
    user = User.get_logged_in(request)

    # Don't allow if logged in
    if user is not None:
        return redirect('dashboard')

    if request.method == 'POST':
        registration_form = RegistrationForm(request.POST)

        if registration_form.is_valid():
            username = registration_form.cleaned_data['username']
            password = registration_form.cleaned_data['password']

            new_user = RegistrationForm(request.POST)
            new_patient = new_user.save()
            new_patient.is_patient = True
            new_patient.is_pending = False
            new_patient.set_password(password)
            new_patient.doctors = registration_form.cleaned_data['doctors']
            new_patient.save()
            Logging.info("User '%s' created" % username)

            if new_user is not None:
                Logging.info("User created with username '%s" % username)
                User.login(request, username, password)
                return HttpResponseRedirect('/dashboard')

            return HttpResponseRedirect('dashboard')
    else:
        registration_form = RegistrationForm(request.POST)

    context = {
        'registration_form': registration_form
    }

    return render(request, 'register.html', context)


def edit_info(request, pk=None):
    """
    User tries to edit their information
    :param request: request to edit their information
    :return: Goes to dashboard if successful, otherwise stays on edit_info with
                a message saying what they need to fix"
    """

    show_name = False

    if pk is None:
        user = User.get_logged_in(request)
        primary_key = user.pk

        # Require login
        if user is None:
            messages.error(request, "You must be logged in to access this page.")
            return redirect('index')

        # Check user type
        if not user.is_type(UserType.Patient):
            messages.error(request, "You must be a patient to edit your information.")
            return redirect('index')
    else:
        show_name = True
        logged = User.get_logged_in(request)
        user = User.objects.get(pk=pk)
        primary_key = pk

        # Require login
        if logged is None:
            messages.error(request, "You must be logged in to access this page.")
            return redirect('index')

        # Check logged type
        if not logged.is_type(UserType.Doctor) and not logged.is_type(UserType.Nurse) or not logged.has_patient(user):
            messages.error(request, "You aren't allowed to view this patient!")
            return redirect('index')

        # Check user type
        if not user.is_type(UserType.Patient):
            messages.error(request, "You must be a patient to edit your information.")
            return redirect('index')

    if request.method == 'POST':
        u = Patient.objects.get(pk=primary_key)
        form = EditPatientInfoForm(request.POST, instance=u)

        if form.is_valid():  # is_valid is function not property
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, "Your profile information has been successfully saved!")
            return redirect('dashboard')
    else:
        u = Patient.objects.get(pk=primary_key)
        form = EditPatientInfoForm(instance=u)  # No request.POST
    # move it outside of else
    context = {
        'show_name': show_name,
        'patient_user': user,
        'edit_info': form
    }
    return user.render_for_user(request, 'edit_user.html', context)


def logout(request):
    """
    User tries to logout
    :param request: request to logout
    :return: goes to index page
    """
    User.logout(request)
    return redirect('index')


def log(request):
    """
    User tries to access the log
    :param request: request to access the log
    :return: If User is noone, they go to the index page
                If they are not an admin, they get denined
                If they are an admin, they got to the log page
    """
    user = User.get_logged_in(request)

    # Require login
    if user is None:
        return redirect('index')

    # Check user type
    if not user.is_type(UserType.Administrator):
        return HttpResponse("Access Denied!")

    context = {
        'log_entries': LogEntry.objects.all()
    }

    return user.render_for_user(request, 'log.html', context)


def cancel_appointment(request, pk):
    """
    User tries to cancel an appointment
    :param request: request to cancel an appointment
    :param pk: They appointment key
    :return: If no User, index page
                Otherwise, go back to the page the user was at before
    """
    user = User.get_logged_in(request)

    # Require login
    if user is None:
        return redirect('index')

    # Get appointment based on pk argument
    apt = Appointment.objects.get(pk=pk)

    # User can only delete if they are an attendee
    if user not in apt.attendees.all():
        messages.error(request, "You aren't allowed to cancel this appointment!")
    else:
        # noinspection PyBroadException
        try:
            apt.delete()
            Logging.info("Appointment with pk '%s' canceled by '%s" % (apt.pk, user.username))
            messages.success(request, "The appointment was successfully deleted!")
        except:
            messages.error(request, "There was an error deleting this appointment!")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def edit_appointment(request, pk):
    """
    User tries to edit an appointment
    :param request: request to edit an appointment
    :param pk: Appointment key
    :return: If ues not logged in, Index page
                Otherwise, the edit_appointment page
    """
    # Show available times for doctor; needs to be more user friendly
    user = User.get_logged_in(request)

    if user is None:
        return redirect('index')

    apt = Appointment.objects.get(pk=pk)

    if user not in apt.attendees.all():
        messages.error(request, "You aren't allowed to cancel this appointment!")
    else:
        if request.method == 'POST':
            form = AppointmentForm(request.POST, instance=apt)

            if form.is_valid():  # is_valid is function not property
                new_apt = form.save(commit=False)
                if new_apt.has_conflict():
                    messages.error(request, "There is a conflict with the selected times!")
                    form = AppointmentForm(instance=apt)
                    apt.save()
                else:
                    new_apt.save()
                    Logging.info("Appointment with pk '%s' edited by '%s" % (apt.pk, user.username))
                    return redirect('dashboard')
        else:
            form = AppointmentForm(instance=apt)  # No request.POST

        # move it outside of else
        context = {
            'apt': apt,
            'appointment_form': form
        }
        return user.render_for_user(request, 'edit_appointment.html', context)


def toggle_admit(request, pk):
    """
    Toggles a users admittance status
    :param request: http request
    :param pk: The patients pk
    :return: If no User, index page
                Otherwise, go back to the page the user was at before
    """
    user = User.get_logged_in(request)

    # Require login
    if user is None:
        return redirect('index')

    # Get patient based on pk argument
    patient = Patient.objects.get(pk=pk)

    # User can only admit if they are nurse or doctor
    if not user.is_type(UserType.Doctor) and not User.is_type(UserType.Nurse) or not user.has_patient(patient):
        messages.error(request, "You aren't allowed to admit/discharge this patient!")
    else:
        # noinspection PyBroadException
        try:
            patient.toggle_admit()
            Logging.info("'%s' admittance status changed to '%s' by '%s'" % (
                patient.username, str(patient.is_admitted), user.username))
            messages.success(request,
                             "The patient was successfully %s!" % ('admitted' if patient.is_admitted else 'discharged'))
        except:
            messages.error(request, "There was an error %s this patient!" % (
                'admitting' if patient.is_admitted else 'discharging'))

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def transfer(request, pk):
    user = User.get_logged_in(request)

    # Require login
    if user is None:
        return redirect('index')

    # Get patient based on pk argument
    patient = Patient.objects.get(pk=pk)

    # User can only transfer if they are nurse or doctor or admin
    if not user.is_type(UserType.Doctor) and not user.is_type(UserType.Nurse) and not user.is_type(UserType.Administrator) or not user.has_patient(patient):
        messages.error(request, "You aren't allowed to transfer this patient!")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        if request.method == 'POST':
            form = TransferForm(request.POST, transferer=user)

            if form.is_valid():
                patient.transfer(form.cleaned_data['transfer_to'])
                Logging.info("Patient '%s' has been transfered to '%s' hospital by user '%s'." % (
                    str(patient), str(form.cleaned_data['transfer_to']), str(user)))
                messages.success(request, "The patient has been transfered!")
                return redirect('dashboard')
        else:
            form = TransferForm(transferer=user)

        context = {
            'current_hospital': str(patient.get_hospitals()[0]) if len(patient.get_hospitals()) > 0 else None,
            'patient_name': patient.get_display_name(),
            'form': form,
        }

        return user.render_for_user(request, 'transfer.html', context)


def toggle_read(request, pk):
    user = User.get_logged_in(request)

    # Require login
    if user is None:
        return redirect('index')

    # Get message based on pk argument
    msg = Message.objects.get(pk=pk)

    # check user can see this message
    if msg.recipient_id is not user.pk:
        messages.error(request, "You aren't allowed to read this message!")
    else:
        msg.toggle_unread()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def approve_user(request, pk):
    user = User.get_logged_in(request)

    # Require login
    if user is None:
        return redirect('index')

    # Get message based on pk argument
    to_approve = User.objects.get(pk=pk)

    # check user can see this message
    if not user.is_type(UserType.Administrator):
        messages.error(request, "You aren't allowed to approve users!")
    else:
        messages.success(request, "%s has been approved." % str(user))
        to_approve.approve()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def send_message(request, pk=None):
    user = User.get_logged_in(request)

    # Require login
    if user is None:
        return redirect('index')

    if request.method == 'POST':
        form = SendMessageForm(request.POST, sender=user, initial={'recipient': pk, 'type': MessageType.Normal})

        if form.is_valid():
            Message.send(user, form.cleaned_data['recipient'], form.cleaned_data['message'], form.cleaned_data['type'])
            messages.success(request, "Your message has been sent!")
            return redirect('inbox')
    else:
        form = SendMessageForm(sender=user, initial={'recipient': pk, 'type': MessageType.Normal})
    context = {
        'is_message_page': True,
        'form': form,
    }

    return user.render_for_user(request, 'send_message.html', context)


def reply_message(request, pk):
    user = User.get_logged_in(request)

    # Require login
    if user is None:
        return redirect('index')

    # Get message based on pk argument
    msg = Message.objects.get(pk=pk)

    # check user can see this message
    if msg.recipient_id is not user.pk:
        messages.error(request, "You aren't allowed to read this message!")
        return redirect('inbox')

    if request.method == 'POST':
        form = ReplyMessageForm(request.POST)

        if form.is_valid():
            recp = msg.sender
            if msg.sender is user:
                recp = msg.recipient

            msg.reply(user, recp, form.cleaned_data['message'])
            messages.success(request, "Your message has been sent!")
            return redirect('inbox')
    else:
        form = ReplyMessageForm()
    context = {
        'is_message_page': True,
        'msg': msg,
        'form': form
    }

    return user.render_for_user(request, 'reply_message.html', context)


def inbox(request):
    user = User.get_logged_in(request)

    # Require login
    if user is None:
        return redirect('index')

    # user.mark_messages_read()

    context = {
        'is_message_page': True,
        'msgs': user.received_messages.order_by('-date')
    }

    return user.render_for_user(request, 'inbox.html', context)


def sent_messages(request):
    user = User.get_logged_in(request)

    # Require login
    if user is None:
        return redirect('index')

    context = {
        'is_message_page': True,
        'is_sent': True,
        'msgs': user.sent_messages.order_by('-date')
    }

    return user.render_for_user(request, 'inbox.html', context)


# DEBUG VIEWS
def create_test_user(request):
    """
    Creates a test patient
    :param request: request to create a test patient
    :return: If not r, returns o
                Else, returns
    """
    r, o = User.create_user('test', 'test', UserType.Patient, 'Test', 'User')
    if not r:
        return HttpResponse(o)
    Logging.warning("Created debug test patient user")
    return HttpResponse("result: %s, obj: %s:" % (str(r), str(o)))


def create_admin_user(request):
    """
    Creates a test admin
    :param request: request to create a test admin
    :return: If not r, returns o
                Else, returns
    """
    r, o = User.create_user('admin', 'admin', UserType.Administrator, 'Admin', 'User')
    if not r:
        return HttpResponse(o)
    Logging.warning("Created debug test admin user")
    return HttpResponse("result: %s, obj: %s:" % (str(r), str(o)))


def create_test_doctor(request):
    """
    Creates a test doctor
    :param request: request to create a test doctor
    :return: If not r, returns o
                Else, returns
    """
    r, o = User.create_user('doctor', 'doctor', UserType.Doctor, 'Doctor', 'House')
    if not r:
        return HttpResponse(o)
    Logging.warning("Created debug test doctor user")
    return HttpResponse("result: %s, obj: %s:" % (str(r), str(o)))


def create_test_nurse(request):
    """
    Creates a test nurse
    :param request: request to create a test nurse
    :return: If not r, returns o
                Else, returns
    """
    r, o = User.create_user('nurse', 'nurse', UserType.Nurse, 'Nurse', 'Sue')
    if not r:
        return HttpResponse(o)
    Logging.warning("Created debug test nurse user")
    return HttpResponse("result: %s, obj: %s:" % (str(r), str(o)))
