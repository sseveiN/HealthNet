import os
import sys
from getpass import getpass
from io import StringIO

import django
from django.core import management
from django.core.management import BaseCommand
from django.db import connection

from healthnet.core.users.user import User, UserType
from django.contrib.auth.models import User as SuperUser

from healthnet.models import Hospital, States


class Command(BaseCommand):
    def confirm(self, s):
        yes = {'yes', 'y', 'ye', ''}
        self.print_ok(s)
        choice = input().lower()
        return choice in yes

    def print_ok(self, s):
        print('\033[92m' + s + '\033[0m')

    def print_err(self, s):
        print('\033[91m' + s + '\033[0m')

    def handle(self, **options):
        # Check we are using the proper python version
        if sys.version_info < (3, 4):
            self.print_err("You must be using Python 3.4 or greater.")
            return

        # Check django version
        if django.VERSION < (1, 9):
            self.print_err("You must be using Django 1.9 or greater.")
            return

        # Make sure its ok that we destroy everything
        if not self.confirm("We're going to destroy all HealthNet data. Is this ok? (Yes, No)"):
            return
        print("\n")

        # destroy database
        buf = StringIO()
        management.call_command('sqlflush', interactive=False, stdout=buf)

        for cmd in buf.getvalue().splitlines():
            connection.cursor().execute(cmd.strip())

        # try:
        #     SuperUser.objects.all().delete()
        #     User.objects.all().delete()
        # except:
        #     pass

        # migrate
        management.call_command('makemigrations', interactive=False, stdout=None)
        management.call_command('migrate', interactive=False, stdout=None)

        # migrate healthnet
        management.call_command('makemigrations', 'healthnet', interactive=False, stdout=None)
        management.call_command('migrate', 'healthnet', interactive=False, stdout=None)
        print("\n")

        # Create super users
        self.print_ok("Create super user for system admin:")
        username = input('Username: ')
        password = getpass('Password: ')
        su = SuperUser.objects.create_superuser(username=username, password=password, email='')
        su.save()
        print("\n")

        # Create first hospital
        self.print_ok("Create the first Hospital:")
        name = input('Hospital Name: ')
        addr_1 = input('Address Line 1: ')
        addr_2 = input('Address Line 2: ')
        city = input('City: ')

        for state_num, state_name in States.get_choices():
            print('%s = %s' % (state_num, state_name))

        state = input('State (number): ')
        zipcode = input('Zipcode: ')
        hospital = Hospital.objects.create(name=name, address_line_1=addr_1, address_line_2=addr_2, city=city,
                                           state=state,
                                           zipcode=zipcode)
        hospital.save()
        print("\n")

        # Create hospital admin
        self.print_ok("Create the admin user for this Hospital:")
        fn = input('First Name: ')
        ln = input('Last Name: ')
        username = input('Username: ')
        password = getpass('Password: ')
        success, admin = User.create_user(username, password, UserType.Administrator, first_name=fn, last_name=ln,
                                          print_stdout=False)

        if not success:
            print("Error creating admin: " + admin)
            return

        admin.hospitals = hospital
        admin.is_pending = False
        admin.save()
        print("\n")

        self.print_ok("Install is complete.")
        self.print_ok("You may now run 'python manage.py runserver'.")
