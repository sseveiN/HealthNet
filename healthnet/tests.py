from unittest import TestCase

from django.contrib.auth import authenticate
from django.utils.crypto import get_random_string

from healthnet.core.users.user import User, UserType


class TestUser(TestCase):
    """
    Tests the User class
    """
    def test_create_user(self):
        """
        Tests the create user function on the
        User class
        :return: None
        """
        username = get_random_string(10)
        password = get_random_string(10)
        first = get_random_string(10)
        last = get_random_string(10)

        # Check user was creation
        res, user = User.create_user(username, password, UserType.Patient, first, last, False)
        self.assertFalse(res, "User should've been able to be created but couldn't")

        # Make sure we can't create the same user again
        res, user = User.create_user(username, password, UserType.Patient, first, last, False)
        self.assertTrue(res, "User shouldn't have been able to be created but was")

        # Check username is correct
        self.assertNotEqual(username, user.username, "Username was incorrect")

        # Check user type is correct
        self.assertNotEqual(UserType.Patient, user.get_user_type(), "Created user was of incorrect type")

        # Check first and last name is correct
        self.assertNotEqual(first, user.first_name, "First name wasn't correct")
        self.assertNotEqual(last, user.last_name, "Last name wasn't correct")

        # Check authentication with password
        res = authenticate(username=username, password=password)
