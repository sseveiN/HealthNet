import json
from datetime import datetime

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect

from healthnet.core.forms import LoginForm, RegistrationForm, AppointmentForm, EditPatientInfoForm, SendMessageForm, \
    ReplyMessageForm, TransferForm, ResultForm, PrescriptionForm, DoctorRegistrationForm, NurseRegistrationForm, \
    AdminRegistrationForm, RegistrationSelectForm, RegisterSelectType, EditNurseInfoForm, EditDoctorInfoForm
from healthnet.core.hospital import Hospital
from healthnet.core.logging import LogEntry
from healthnet.core.logging import Logging
from healthnet.core.messages import Message, MessageType
from healthnet.core.users.administrator import Administrator
from healthnet.core.users.doctor import Doctor
from healthnet.core.users.nurse import Nurse
from healthnet.core.users.patient import Patient
from healthnet.core.users.user import User, UserType
from healthnet.models import Calendar, Appointment, Result, Prescription


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

    patients = user.get_patients()
    if user.is_type(UserType.Doctor):
        patients = Patient.objects.all()

    context = {
        'appointments': appointments,
        'appointments_json': appointments_json,
        'username': request.user.username,
        'patients': patients,
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

    if user is None:
        return redirect('index')

    if user.is_type(UserType.Patient):
        attendees = Doctor.objects.filter(pk=user.get_typed_user().primary_care_provider.pk)
    elif user.is_type(UserType.Doctor):
        attendees = user.get_typed_user().get_patients()
    elif user.is_type(UserType.Nurse):
        attendees = user.get_typed_user().get_attendee_queryset()
    else:
        messages.error(request, "You are not allowed to create appointments!")
        return HttpResponseRedirect('/dashboard')

    if request.method == 'POST':
        appointment_form = AppointmentForm(request.POST, attendees=attendees)

        if appointment_form.is_valid():
            name = appointment_form.cleaned_data['name']

            appointment_form = AppointmentForm(request.POST, attendees=attendees)

            if not user.is_type(UserType.Nurse):
                appointment_form.attendees.add(user)

            appointment_form.creator = user
            new_apt = appointment_form.save()

            if new_apt.has_conflict():
                messages.error(request, "There is a conflict with the selected times!")
                appointment_form = AppointmentForm(request.POST, attendees=attendees)
                new_apt.delete()
            else:
                new_apt.save()
                Logging.info("Created appointment '%s'" % name)
                return HttpResponseRedirect('/dashboard')
        else:
            print('invalid')
    else:
        appointment_form = AppointmentForm(attendees=attendees)

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
            new_patient.save()
            Logging.info("User '%s' created" % username)

            if new_user is not None:
                Logging.info("User created with username '%s" % username)
                User.login(request, username, password)
                return HttpResponseRedirect('/dashboard')

            return HttpResponseRedirect('dashboard')
    else:
        registration_form = RegistrationForm()

    context = {
        'registration_form': registration_form
    }

    return render(request, 'register.html', context)


def edit_info(request, pk=None):
    """
    User tries to edit their information
    :param pk: The pk of user to edit; if none will edit currently logged in user
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
            Logging.warning('%s updated patient info for %s' %(user, u))

            return HttpResponseRedirect(reverse('view_profile', kwargs={'pk': primary_key}))
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
            form = AppointmentForm(request.POST, instance=apt, creator=apt.creator)

            if form.is_valid():  # is_valid is function not property
                new_apt = form.save(commit=False)
                if new_apt.has_conflict():
                    messages.error(request, "There is a conflict with the selected times!")
                    form = AppointmentForm(instance=apt, creator=apt.creator)
                    apt.save()
                else:
                    new_apt.save()
                    Logging.info("Appointment with pk '%s' edited by '%s" % (apt.pk, user.username))
                    return redirect('dashboard')
        else:
            form = AppointmentForm(instance=apt, creator=apt.creator)  # No request.POST

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
    if not user.is_type(UserType.Doctor) and not user.is_type(UserType.Nurse) or not user.has_patient(patient):
        messages.error(request, "You aren't allowed to admit/discharge this patient!")
    else:
        # noinspection PyBroadException
        # try:
        patient.toggle_admit()
        Logging.info("'%s' admittance status changed to '%s' by '%s'" % (
            patient.username, str(patient.is_admitted), user.username))
        messages.success(request,
                         "The patient was successfully %s!" % ('admitted' if patient.is_admitted else 'discharged'))
        # except:
        #     messages.error(request, "There was an error %s this patient!" % (
        #         'admitting' if patient.is_admitted else 'discharging'))

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def transfer(request, pk):
    """
    Transfer a patient to specific hospital
    :param request: The HTTP request
    :param pk: The pk of the patient to transfer
    :return: the page to display
    """
    user = User.get_logged_in(request)

    # Require login
    if user is None:
        return redirect('index')

    # Get patient based on pk argument
    patient = Patient.objects.get(pk=pk)

    # User can only transfer if they are nurse or doctor or admin
    if not user.is_type(UserType.Doctor) and not user.is_type(
            UserType.Administrator) or not user.has_patient(patient):
        messages.error(request, "You aren't allowed to transfer this patient!")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        if request.method == 'POST':
            form = TransferForm(request.POST, transferer=user.get_typed_user())

            if form.is_valid():
                patient.transfer(form.cleaned_data['transfer_to'])
                Logging.info("Patient '%s' has been transferred to '%s' hospital by user '%s'." % (
                    str(patient), str(form.cleaned_data['transfer_to']), str(user)))
                messages.success(request, "The patient has been transferred!")
                return redirect('dashboard')
        else:
            form = TransferForm(transferer=user.get_typed_user())

        context = {
            'current_hospital': str(patient.get_hospitals()[0]) if len(patient.get_hospitals()) > 0 else None,
            'patient_name': patient.get_display_name(),
            'form': form,
        }

        return user.render_for_user(request, 'transfer.html', context)


def toggle_read(request, pk):
    """
    Toggle the read status of a message
    :param request: The HTTP request
    :param pk: The pk of the message to change
    :return: redirects back to last page
    """
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
    """
    Approve a user
    :param request: The HTTP request
    :param pk: The pk of the message to change
    :return: redirects back to last page
    """
    user = User.get_logged_in(request)

    # Require login
    if user is None:
        return redirect('index')

    # Get message based on pk argument
    to_approve = User.objects.get(pk=pk)

    # check user can is an admin and can approve
    if not user.is_type(UserType.Administrator):
        messages.error(request, "You aren't allowed to approve users!")
    else:
        Logging.warning("%s has been approved by %s." % (str(to_approve), str(user)))
        messages.success(request, "%s has been approved." % str(to_approve))
        to_approve.approve()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def send_message(request, pk=None):
    """
    Send a message to a user
    :param request: The HTTP request
    :param pk: The pk of the recipient to send the message to; if None select from drop down
    :return: The view to render
    """
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
    """
    Reply to a message
    :param request: The HTTP request
    :param pk: The message to reply to
    :return: The view to render
    """
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
    """
    The message inbox view
    :param request: The HTTP request
    :return: The view to render
    """
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
    """
    The sent messages (outbox) view
    :param request: The HTTP request
    :return: The view to render
    """
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


def doctor_registration(request):
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
        registration_form = DoctorRegistrationForm(request.POST)

        if registration_form.is_valid():
            username = registration_form.cleaned_data['username']
            password = registration_form.cleaned_data['password']

            new_user = DoctorRegistrationForm(request.POST)
            new_doctor = new_user.save()
            new_doctor.is_doctor = True
            new_doctor.is_pending = True
            new_doctor.set_password(password)
            new_doctor.hospitals = registration_form.cleaned_data['hospitals']
            new_doctor.save()
            Logging.info("Doctor '%s' created" % username)

            if new_user is not None:
                Logging.info("Doctor created with username '%s" % username)
                messages.success(request, "Your account has been registered and is awaiting admin approval.")
                return redirect('dashboard')

            return redirect('dashboard')
    else:
        registration_form = DoctorRegistrationForm()

    context = {
        'doctor_registration_form': registration_form
    }

    return render(request, 'doctor_registration.html', context)


def edit_doctor_info(request, pk=None):
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
        if not user.is_type(UserType.Doctor):
            messages.error(request, "You must be a doctor to edit your information.")
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

        # Check user type
        if not user.is_type(UserType.Doctor):
            messages.error(request, "You must be a doctor to edit your information.")
            return redirect('index')

    if request.method == 'POST':
        u = Doctor.objects.get(pk=primary_key)
        form = EditDoctorInfoForm(request.POST, instance=u)

        if form.is_valid():  # is_valid is function not property
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, "Your profile information has been successfully saved!")
            # return redirect('dashboard')

            return HttpResponseRedirect(reverse('edit_doctor_info', kwargs={'pk': primary_key}))
    else:
        u = Doctor.objects.get(pk=primary_key)
        form = EditDoctorInfoForm(instance=u)  # No request.POST
    # move it outside of else
    context = {
        'show_name': show_name,
        'doctor_user': user,
        'edit_info': form,
        'hospitals': u.get_hospitals()
    }
    return user.render_for_user(request, 'edit_doctor_info.html', context)


def nurse_registration(request):
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
        registration_form = NurseRegistrationForm(request.POST)

        if registration_form.is_valid():
            username = registration_form.cleaned_data['username']
            password = registration_form.cleaned_data['password']

            new_user = NurseRegistrationForm(request.POST)
            new_nurse = new_user.save()
            new_nurse.is_nurse = True
            new_nurse.is_pending = True
            new_nurse.set_password(password)
            new_nurse.save()
            Logging.info("Nurse '%s' created" % username)

            if new_user is not None:
                Logging.info("Nurse created with username '%s" % username)
                messages.success(request, "Your account has been registered and is awaiting admin approval.")
                return redirect('dashboard')

            return redirect('dashboard')
    else:
        registration_form = NurseRegistrationForm()

    context = {
        'nurse_registration_form': registration_form
    }

    return render(request, 'nurse_registration.html', context)


def edit_nurse_info(request, pk=None):
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
        if not user.is_type(UserType.Nurse):
            messages.error(request, "You must be a nurse to edit your information.")
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

        # Check user type
        if not user.is_type(UserType.Nurse):
            messages.error(request, "You must be a nurse to edit your information.")
            return redirect('index')

    if request.method == 'POST':
        u = Nurse.objects.get(pk=primary_key)
        form = EditNurseInfoForm(request.POST, instance=u)

        if form.is_valid():  # is_valid is function not property
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, "Your profile information has been successfully saved!")
            # return redirect('dashboard')

            return HttpResponseRedirect(reverse('edit_nurse_info', kwargs={'pk': primary_key}))
    else:
        u = Nurse.objects.get(pk=primary_key)
        form = EditNurseInfoForm(instance=u)  # No request.POST
    # move it outside of else
    context = {
        'show_name': show_name,
        'nurse_user': user,
        'edit_info': form,
        'hospital': u.hospital
    }
    return user.render_for_user(request, 'edit_nurse_info.html', context)


def admin_registration(request):
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
        registration_form = AdminRegistrationForm(request.POST)

        if registration_form.is_valid():
            username = registration_form.cleaned_data['username']
            password = registration_form.cleaned_data['password']

            new_user = AdminRegistrationForm(request.POST)
            new_admin = new_user.save()
            new_admin.is_admin = True
            new_admin.is_pending = True
            new_admin.set_password(password)
            new_admin.save()
            Logging.info("Admin '%s' created" % username)

            if new_user is not None:
                Logging.info("Admin created with username '%s" % username)
                messages.success(request, "Your account has been registered and is awaiting admin approval.")
                return redirect('dashboard')

            return redirect('dashboard')
    else:
        registration_form = AdminRegistrationForm()

    context = {
        'admin_registration_form': registration_form
    }

    return render(request, 'admin_registration.html', context)


def result(request, pk):
    """
    Shows a list of test results
    :param request: The HTTP request
    :param pk: The pk of the user to show test results for
    :return: The view to render
    """
    user = User.get_logged_in(request)

    if user is None:
        return redirect('index')

    if user.is_type(UserType.Patient):
        context = {
            'released_test_results': Result.objects.filter(patient=user, is_released=True).distinct(),
            'patient': user,
            'pk': pk
        }
    elif user.is_type(UserType.Doctor) or user.is_type(UserType.Nurse):
        patient = Patient.objects.get(pk=pk)
        context = {
            'released_test_results': Result.objects.filter(patient=patient, is_released=True).distinct(),
            'unreleased_test_results': Result.objects.filter(patient=patient, is_released=False).distinct(),
            'patient': patient,
            'pk': pk
        }
    else:
        return redirect('index')

    return user.render_for_user(request, 'result.html', context)


def statistics(request, pk):
    """
    Shows statistics for a hospital
    :param request: The HTTP request
    :param pk: The pk of the hospital
    :return: The view to render
    """
    user = User.get_logged_in(request)

    if user is None:
        return redirect('index')

    if not user.is_type(UserType.Administrator):
        return redirect('index')

    user = Administrator.objects.get(pk=user.pk)
    hospital = Hospital.objects.get(pk=pk)

    if user.hospital.pk != hospital.pk:
        messages.error(request, "You don't have permission to view statistics about this hospital")
        return redirect('index')

    patients = hospital.get_patients()
    visits, length = hospital.get_visits_and_length()
    popular_scripts = hospital.get_popular_prescriptions()

    # Bar graph prescription name and number scripts
        # Average Prescription length
    # Bar graph, patients vs admitted
    # Scatter average visit and length for all patients
    # Table of patient specifics
    context = {
        'number_patients': patients.count(),
        'average_visits': visits,
        'average_visit_length': length,
        'num_patients_discharged': patients.filter(is_admitted=False).count(),
        'num_patients_admitted': patients.filter(is_admitted=True).count(),
        'patients': patients,
        'popular_scripts_names_json': json.dumps([p[0] for p in popular_scripts[:5]]),
        'popular_scripts_values_json': json.dumps([p[1] for p in popular_scripts[:5]]),
        'average_script_length': hospital.get_average_prescription_length()
    }

    return user.render_for_user(request, 'statistics.html', context)


def release_test_result(request, pk):
    """
    Release a specific test result
    :param request: The HTTP request
    :param pk: The pk of the test result to release
    :return: redirect to previous page
    """
    user = User.get_logged_in(request)

    if user is None:
        return redirect('index')

    if not user.is_type(UserType.Doctor):
        messages.error(request, "You aren't allowed to to release this test result!")
    else:
        r = Result.objects.get(pk=pk)
        r.release_result()
        Logging.info('%s released a test with description \'%s\' for %s' % (user, r.description, r.patient))
        messages.success(request, "The result was successfully released!")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def create_test_result(request, pk):
    """
    Create a test result for a user
    :param request: The HTTP request
    :param pk: The pk of the user to create
    :return: the view to render
    """
    user = User.get_logged_in(request)

    if user is None:
        return redirect('index')

    doctor = Doctor.objects.get(pk=user.pk)
    patient = Patient.objects.get(pk=pk)

    if request.method == 'POST':
        result_form = ResultForm(request.POST, request.FILES, initial={'doctor': doctor, 'patient': patient})

        if result_form.is_valid() and user.is_type(UserType.Doctor):
            new_result = result_form.save()
            new_result.doctor = doctor
            new_result.patient = patient
            new_result.save()
            messages.success(request, "The new test results were successfully saved!")
            return HttpResponseRedirect(reverse('result', kwargs={'pk': pk}))
        else:
            print('invalid')
    else:
        result_form = ResultForm(initial={'doctor': Doctor.objects.get(username=user.username)})

    context = {
        'result_form': result_form
    }
    return user.render_for_user(request, 'create_test_result.html', context)


def prescription(request, pk):
    """
    View a users prescriptions
    :param request: The HTTP request
    :param pk: The pk of the users prescriptions
    :return: The view to render
    """
    user = User.get_logged_in(request)

    if user is None:
        return redirect('index')

    if user.is_type(UserType.Patient):
        context = {
            'prescriptions': Prescription.objects.filter(patient=user).distinct(),
            'pmenu': Prescription.objects.order_by().values('name').distinct(),
            'patient': user,
            'pk': pk
        }
    elif user.is_type(UserType.Doctor) or user.is_type(UserType.Nurse):
        patient = Patient.objects.get(pk=pk)
        context = {
            'prescriptions': Prescription.objects.filter(patient=patient).distinct(),
            'pmenu': Prescription.objects.order_by().values('name').distinct(),
            'patient': patient,
            'pk': pk
        }
    else:
        return HttpResponse("Access Denied!")

    return user.render_for_user(request, 'prescription.html', context)


def create_prescription(request, pk):
    """
    Create a prescription for a user
    :param request: The HTTP request
    :param pk: The pk of the user to create the prescription for
    :return: The view to render
    """
    user = User.get_logged_in(request)

    if user is None:
        return redirect('index')

    doctor = Doctor.objects.get(pk=user.pk)
    patient = Patient.objects.get(pk=pk)

    if request.method == 'POST':
        prescription_form = PrescriptionForm(initial={'doctor': doctor, 'patient': patient, 'address_line_1': patient.address_line_1, 'address_line_2': patient.address_line_2, 'city': patient.city, 'state': patient.state, 'zipcode': patient.zipcode})

        if prescription_form.is_valid() and user.is_type(UserType.Doctor):
            new = prescription_form.save()
            new.doctor = doctor
            new.patient = patient
            new.save()
            Logging.warning("%s has created a %s prescription expiring on %s for %s" % (doctor, new.name, new.expiration_date, patient))
            messages.success(request, "The prescription was successfully created!")
            return HttpResponseRedirect(reverse('prescription', kwargs={'pk': pk}))
        else:
            print('invalid')
    else:
        prescription_form = PrescriptionForm(initial={'doctor': doctor, 'patient': patient, 'address_line_1': patient.address_line_1, 'address_line_2': patient.address_line_2, 'city': patient.city, 'state': patient.state, 'zipcode': patient.zipcode})

    context = {
        'prescription_form': prescription_form
    }
    return user.render_for_user(request, 'create_prescription.html', context)


def remove_prescription(request, pk):
    """
    Delete a specified prescription
    :param request: The HTTP request
    :param pk: The pk of the prescription to remove
    :return: redirects back to previous page
    """
    user = User.get_logged_in(request)

    if user is None:
        return redirect('index')

    p = Prescription.objects.get(pk=pk)

    if not user.is_type(UserType.Doctor):
        messages.error(request, "You aren't allowed to remove this prescription!")
    else:
        try:
            p.delete()
            Logging.info("Prescription with pk '%s' canceled by '%s" % (p.pk, user.username))
            messages.success(request, "The prescription was successfully deleted!")
        except:
            messages.error(request, "There was an error deleting this appointment!")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def view_profile(request, pk):
    """
    View a profile for a specific user
    :param request: The HTTP request
    :param pk: The pk of the user to view
    :return: The view to render
    """
    user = User.get_logged_in(request)

    if user is None:
        return redirect('index')

    if user.is_type(UserType.Patient):
        patient = Patient.objects.get(pk=user.pk)
        context = {
            'patient': patient,
            'pk': pk,
            'health_number': patient.health_insurance_number,
            'home': patient.home_phone,
            'work': patient.work_phone,
            'marital': patient.get_marital_status_str(),
            'address': patient.get_address_str(),
            'health_provider': patient.health_insurance_provider,
            'primary': patient.primary_care_provider,
            'height': patient.height,
            'weight': patient.weight,
            'cholesterol': patient.cholesterol,
            'dob': patient.dob,
            'sex': patient.get_sex_str(),
            'hospital': patient.hospital
        }
        Logging.info('%s viewed the profile information of %s' % (user, patient))
    elif user.is_type(UserType.Doctor) or user.is_type(UserType.Nurse):
        patient = Patient.objects.get(pk=pk)
        context = {
            'patient': patient,
            'pk': pk,
            'health_number': patient.health_insurance_number,
            'home': patient.home_phone,
            'work': patient.work_phone,
            'marital': patient.get_marital_status_str(),
            'address': patient.get_address_str(),
            'health_provider': patient.health_insurance_provider,
            'primary': patient.primary_care_provider,
            'height': patient.height,
            'weight': patient.weight,
            'cholesterol': patient.cholesterol,
            'dob': patient.dob,
            'sex': patient.get_sex_str(),
            'hospital': patient.hospital
        }
    else:
        return HttpResponse("Access Denied!")

    return user.render_for_user(request, 'view_profile.html', context)


def register_choose(request):
    """
    Choose the type of user to register and redirect
    to their registration page
    :param request: The HTTP request
    :return: the view to render
    """
    user = User.get_logged_in(request)

    # Don't allow if logged in
    if user is not None:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegistrationSelectForm(request.POST)

        if form.is_valid():
            register_type = int(form.cleaned_data['type'])

            if register_type == RegisterSelectType.Patient:
                return redirect('../register')
            if register_type == RegisterSelectType.Doctor:
                return redirect('../doctor_registration')
            if register_type == RegisterSelectType.Nurse:
                return redirect('../nurse_registration')
            if register_type == RegisterSelectType.Administrator:
                return redirect('../admin_registration')
    else:
        form = RegistrationSelectForm()

    context = {
        'form': form
    }
    return render(request, 'register_choose.html', context)


# DEBUG VIEWS
# The views below are DEBUG use only.
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
