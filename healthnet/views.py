from datetime import datetime

from django.contrib import messages
from django.contrib.auth import authenticate
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from healthnet.core.forms import LoginForm, RegistrationForm, AppointmentForm, EditPatientInfoForm, ResultForm
from healthnet.core.logging import LogEntry
from healthnet.core.users.user import User, UserType
from healthnet.core.users.patient import Patient
from healthnet.core.users.doctor import Doctor
from healthnet.models import Calendar, Appointment, Result
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
                # creds valid; redirect to dashboard
                return HttpResponseRedirect('dashboard')
            else:
                # TODO: error msg
                pass
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

    context = {
        'appointments': appointments,
        'appointments_json': appointments_json,
        'username': request.user.username
    }

    return render(request, 'dashboard.html', context)


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
            me = Patient.objects.get(pk=primary_key)
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
    return render(request, 'appointment.html', context)


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
            new_patient.set_password(password)
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


def edit_info(request):
    """
    User tries to edit their information
    :param request: request to edit their information
    :return: Goes to dashboard if successful, otherwise stays on edit_info with
                a message saying what they need to fix"
    """
    all_pats = Patient.objects.all()
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
        'edit_info': form
    }
    return render(request, 'edit_user.html', context)


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

    return render(request, 'log.html', context)


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
        return render(request, 'edit_appointment.html', context)


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

def result(request):

    user = User.get_logged_in(request)

    if user is None:
        return redirect('index')

    if user.is_type(UserType.Patient):
        context = {
            'released_test_results': Result.objects.filter(patient=user, is_released=True).distinct(),
        }
    elif user.is_type(UserType.Doctor):
        context = {
            'released_test_results': Result.objects.filter(doctor=user, is_released=True).distinct(),
            'unreleased_test_results': Result.objects.filter(doctor=user, is_released=False).distinct(),
        }
    else:
        return HttpResponse("Access Denied!")

    return render(request, 'result.html', context)

def release_test_result(request, pk):
    """
    Doctor tries to release a test result
    :param request: request to cancel an appointment
    :param pk: They result key
    :return: If no User, index page
                Otherwise, go back to the page the user was at before
    """
    user = User.get_logged_in(request)

    # Require login
    if user is None:
        return redirect('index')

    # Get appointment based on pk argument

    # User can only delete if they are an attendee
    if not user.is_type(UserType.Doctor):
        messages.error(request, "You aren't allowed to to release this test result!")
    else:
        # noinspection PyBroadException

            r = Result.objects.get(pk=pk)
            r.release_result()
            #Logging.info("Result with pk '%s' canceled by '%s" % (r.pk, user.username))
            messages.success(request, "The result was successfully released!")

            #messages.error(request, "There was an error releasing this result!")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def create_test_result(request):
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
        result = Result.create_result(user)
        result_form = ResultForm(request.POST, instance=result, initial={'doctor': Doctor.objects.get(username=user.username)})

        if result_form.is_valid() and user.is_type(UserType.Doctor):
            #name = result_form.cleaned_data['name']
            #description = result_form.cleaned_data['description']
            #tstart = result_form.cleaned_data['tstart']
            #tend = result_form.cleaned_data['tend']
            #attendees = result_form.cleaned_data['attendees']

            result_form = ResultForm(request.POST)
            new_result = result_form.save()
            #new_result.doctor = user
            #new_result.is_released = False

            #me = Patient.objects.get(pk=primary_key)
            #new_apt.attendees.add(me)

            #if new_apt.has_conflict():
            #    messages.error(request, "There is a conflict with the selected times!")
            #    appointment_form = AppointmentForm(request.POST)
            #    new_apt.delete()
            #else:
            new_result.save()
            #Logging.info("Created appointment '%s'" % name)
            return HttpResponseRedirect('/result')
        else:
            print('invalid')
    else:
        result_form = ResultForm(request.POST, initial={'doctor': Doctor.objects.get(username=user.username)})

    context = {
        'result_form': result_form
    }
    return render(request, 'create_test_result.html', context)