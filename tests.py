"""This module provides unittest classes for testing of Session, Client and Reservation classes."""

import csv
import json
import os
import sys
import unittest
from datetime import datetime, timedelta, time
from io import StringIO
from unittest.mock import patch, MagicMock

from reservation import Reservation, Client
from session import Session


class TestClient(unittest.TestCase):
    """An unittest class for testing the Client class."""

    @classmethod
    def setUpClass(cls):
        cls.client = Client("John Doe")
        cls.today = datetime.now().date()

    def setUp(self):
        self.this_week_start = (self.today - timedelta(days=self.today.weekday()))
        self.next_week_start = self.this_week_start + timedelta(days=8) - timedelta(
            days=self.this_week_start.weekday())

    def tearDown(self):
        self.client.reservation.clear()

    def test_list_of_client(self):
        """Test the list_of_client method of the Client class."""

        list_of_clients = self.client.list_of_client()
        self.assertEqual(list_of_clients, [self.client])

    def test_make_reservation_success(self):
        """Test the make_reservation method of the Client class for a successful reservation."""

        with patch('builtins.input', return_value='3'):
            result = self.client.make_reservation(self.next_week_start, time(23, 30))
            self.assertTrue(result)  # Should succeed since there is an available slot

    def test_make_reservation_with_two_reservations_fail(self):
        """Test the make_reservation method of the Client class for a failure
        when there are already two reservations on the same week.
        """

        self.client.reservation = [Reservation(self.client, self.next_week_start, time(10, 0)),
                                   Reservation(self.client, self.next_week_start, time(12, 0))]
        with patch('builtins.input', return_value='3'):
            result = self.client.make_reservation(self.next_week_start, time(13, 0))
            self.assertFalse(result)

    def test_make_reservation_in_past_fail(self):
        """Test the make_reservation method of the Client class for a failure when
        the reservation is in the past.
        """

        with patch('builtins.input', return_value='3'):
            result = self.client.make_reservation(self.this_week_start, time(11, 0))
            self.assertFalse(result)

    def test_make_reservation_not_vacant_another_time_true(self):
        """Test the make_reservation method of the Client class for a successful reservation
        when there the given time is already occupied. The method allows to book next available time."""

        self.client.reservation = [Reservation(self.client, self.next_week_start, time(10, 0))]
        with patch('builtins.input', side_effect=['yes', '3']):
            result = self.client.make_reservation(self.next_week_start, time(10, 30))
            self.assertTrue(result)

    def test_make_reservation_less_than_one_hour_fail(self):
        """Test the make_reservation method of the Client class for a failure
        when the reservation is less than an hour away from the current time.
        """

        result = self.client.make_reservation(self.today, (datetime.now() - timedelta(minutes=30)).time())
        self.assertFalse(result)

    def test_cancel_reservation(self):
        """Test the cancel_reservation method of the Client class."""

        reservation = Reservation(self.client, self.today, time(23, 30))
        self.client.reservation.append(reservation)
        with patch('builtins.input', return_value='y'):
            result = self.client.cancel_reservation(self.today)

        self.assertTrue(result)
        self.assertNotIn(reservation, self.client.reservation)
        self.assertNotIn(reservation, Reservation.list_of_reservations())

    def test_cancel_reservation_no_reservation(self):
        """Test the cancel_reservation method of the Client class for a failure when there
         is no reservation on the chosen date.
         """

        with patch('builtins.input', return_value='y'):
            result = self.client.cancel_reservation(self.today)
        self.assertFalse(result)


class TestSession(unittest.TestCase):
    """An unittest class for testing the Session class."""
    @classmethod
    def setUpClass(cls):
        cls.session = Session()

    def capture_output(self, function, expected_output, *args):
        """To capture output of other methods."""

        stdout = sys.stdout
        captured_output = StringIO()
        sys.stdout = captured_output
        # Call the function that expects user input
        function(*args)
        captured_output.seek(0)
        output = captured_output.read()
        # Restore stdout
        sys.stdout = stdout
        # Compare output
        self.assertEqual(output.strip(), expected_output)
        return output

    def test_main_proceed(self):
        """Test of the main method of Session class. T
        he client successfully entered his credentials and allowed to proceed.
        """

        expected_output = "Welcome, Thomas Anderson!\n" \
                          "Thank you for choosing our tennis club.\n\n" \
                          "Goodbye. See you again soon."

        with patch('builtins.input', side_effect=['1', 'Thomas Anderson', '5', '2']):
            self.capture_output(self.session.main, expected_output)

    def test_main_exit(self):
        """Test of the main method of Session class.
        The client chooses to exit.
        """

        expected_output = "Goodbye. See you again soon."
        with patch('builtins.input', return_value='2'):
            self.capture_output(self.session.main, expected_output)

    def test_greeting_valid_name(self):
        """Test of the greeting method of Session class. The client entered valid name."""

        expected_output = "Welcome, Mario Molina!"

        with patch('builtins.input', return_value="Mario Molina"):
            self.capture_output(self.session.greeting, expected_output)

    def test_greeting_invalid_name(self):
        """Test of the greeting method of Session class. The client entered invalid
        name and surname two times.
        """

        expected_output = "Please write your name and surname.\n"\
                          "Please write your name and surname.\n" \
                          "Welcome, Rtwo Dtwo!"

        with patch('builtins.input', side_effect=['R2 D2', 'Rtwo-Dtwo', 'Rtwo Dtwo']):
            self.capture_output(self.session.greeting, expected_output)

    def test_greeting_name_format(self):
        """Test of the greeting method of Session class.
        The format of the name successfully standardized after input.
        """

        expected_output = "Welcome, John Smith!"
        with patch('builtins.input', return_value=' john smith '):
            self.capture_output(self.session.greeting, expected_output)
            result = self.session.greeting()
            self.assertEqual(result.name, "John Smith")

    def test_greeting_new_client(self):
        """Test of the greeting method of the Session class correctly
        creates a new client instance when the user is a new client.
        """

        name = "John Doe"
        expected_output = "Welcome, John Doe!"
        # Mock user input
        with patch('builtins.input', return_value=name):
            with patch.object(Client, 'list_of_client', return_value=[]):
                self.capture_output(self.session.greeting, expected_output)
                result = self.session.greeting()
                self.assertIsInstance(result, Client)
                self.assertEqual(result.name, name)

    def test_greeting_existing_client(self):
        """Test that the greeting method of the Session class correctly
        retrieves an existing client instance when the user is an existing client.
        """

        name = "Jane Doe"
        expected_output = "Welcome back, Jane Doe!"
        # Mock user input
        client = Client(name)
        with patch('builtins.input', return_value=name):
            with patch.object(Client, 'list_of_client', return_value=[client]):
                self.capture_output(self.session.greeting, expected_output)
                result = self.session.greeting()
                self.assertIsInstance(result, Client)
                self.assertEqual(result.name, name)

    def test_session_make_reservation_valid(self):
        """This method tests that the _session_make_reservation method of the
        Session class executes correctly when the user inputs a valid reservation date and time.
        """

        # Create a mock client instance
        client = MagicMock()

        # Test valid input
        date_input = '15.03.2099 15:30'
        expected_date = datetime.strptime(date_input, "%d.%m.%Y %H:%M").date()
        expected_time = datetime.strptime(date_input, "%d.%m.%Y %H:%M").time()

        # Mock user input and client.make_reservation() method
        with patch('builtins.input', return_value=date_input):
            client.make_reservation.return_value = True

            # Call the _session_make_reservation method
            result = self.session._session_make_reservation(client)

            # Assert client.make_reservation() was called with expected arguments
            client.make_reservation.assert_called_once_with(expected_date, expected_time)

            # Assert the method returned True
            self.assertTrue(result)

    def test_session_make_reservation_invalid_date(self):
        """This method tests that the _session_make_reservation method of the Session class
        executes correctly when the user inputs an invalid reservation date and time.
        """

        # Create a mock client instance
        client = MagicMock()

        # Test invalid input
        date_input = '15.03.2099'
        expected_output = "Please check the format of your date and time. " \
                          "Reservations must be made in DD.MM.YYYY HH:MM format."

        # Mock user input
        with patch('builtins.input', return_value=date_input):
            self.capture_output(self.session._session_make_reservation, expected_output, client)
            # Call the method
            result = self.session._session_make_reservation(client)

            # Assert client.make_reservation() was not called
            client.make_reservation.assert_not_called()

            # Assert the method returned False
            self.assertFalse(result)

    def test_valid_date(self):
        """This method tests that the _date_valid method of the Session class
        returns a valid date object when passed a valid date string.
        """

        date_str = "15.03.2099"
        expected_output = datetime.strptime(date_str, "%d.%m.%Y").date()
        result = self.session._date_valid(date_str)
        self.assertEqual(result, expected_output)

    def test_invalid_date_format(self):
        """Tests that the _date_valid method of the Session class
        returns False when passed an invalid date string.
        """

        date_str = "15/03/2099"
        result = self.session._date_valid(date_str)
        self.assertFalse(result)

        date_str = "15-03-2023"
        result = self.session._date_valid(date_str)
        self.assertFalse(result)


class TestReservation(unittest.TestCase):
    """A class that contains unittests for the Reservation class."""

    def setUp(self):
        self.client = Client("John Doe")
        self.today = datetime.now().date()
        self.client.reservation = Reservation(self.client, self.today, time(10, 0), time(11, 0))

    def tearDown(self):
        Reservation.list_of_reservations().clear()
        del self.client

    def test_list_of_reservations(self):
        """Test if the list_of_reservations method returns the list of reservations."""

        start_time = time(11, 0)
        reservation = Reservation(self.client, self.today, start_time)
        self.assertIn(reservation, Reservation.list_of_reservations())
        Reservation.list_of_reservations().remove(reservation)

    def test_reservation_creation_with_end_time(self):
        """Test if reservation creation with end time is working as expected."""

        start_time = time(12, 0)
        end_time = time(12, 30)
        reservation = Reservation(self.client, self.today, start_time, end_time)

        self.assertIsInstance(reservation, Reservation)
        self.assertEqual(reservation.client, self.client)
        self.assertEqual(reservation.date, self.today)
        self.assertEqual(reservation.start_time, start_time)
        self.assertEqual(reservation.end_time, end_time)
        Reservation.list_of_reservations().remove(reservation)

    def test_reservation_creation_without_time(self):
        """Test if reservation creation without end time is working as expected."""

        start_time = time(10, 0)
        end_time = time(11, 00)
        reservation = Reservation(self.client, self.today, start_time)
        self.assertIsInstance(reservation, Reservation)
        self.assertEqual(reservation.client, self.client)
        self.assertEqual(reservation.date, self.today)
        self.assertEqual(reservation.start_time, start_time)
        self.assertEqual(reservation.end_time, end_time)
        Reservation.list_of_reservations().remove(reservation)

    def test_is_valid_file_name(self):
        """Test of the is_valid_file_name method"""

        self.assertTrue(Reservation.is_valid_file_name("file-name"))
        self.assertFalse(Reservation.is_valid_file_name("?file-name"))
        self.assertFalse(Reservation.is_valid_file_name("/file:name"))
        self.assertFalse(Reservation.is_valid_file_name("\\file:name"))
        self.assertFalse(Reservation.is_valid_file_name("*file:name"))
        self.assertFalse(Reservation.is_valid_file_name("    file:name"))

    def test_serialize_to_json(self):
        """Test of the serialize_to_json method. Checked if data is serialized to JSON format
        and stored into a file correctly.
        """

        data = {self.today: [(self.client.name, self.client.reservation.start_time,
                              self.client.reservation.end_time)]}

        with patch('builtins.input', return_value='test_file'):
            Reservation.serialize_to_json(data)

        with open('test_file.json', 'r', encoding='utf-8') as test_file:
            result = json.load(test_file)

        expected = {self.today.strftime("%d.%m"): [
            {"name": self.client.name, "start_time": self.client.reservation.start_time.strftime("%H:%M"),
             "end_time": self.client.reservation.end_time.strftime("%H:%M")}]}
        self.assertEqual(result, expected)
        os.remove("test_file.json")
        print("test_serialize_to_json", Reservation.list_of_reservations())

    def test_write_to_csv(self):
        """Test of the write_to_csv method. Checked if data is stored in CSV format as expected."""

        data = {self.today: ((self.client.name, self.client.reservation.start_time,
                              self.client.reservation.end_time), )}
        with patch('builtins.input', return_value='test_file'):
            Reservation.write_to_csv(data)

        with open('test_file.csv', 'r', encoding='utf-8') as test_file:
            reader = csv.DictReader(test_file)
            result = list(reader)

        expected_output = [
            {
                'name': self.client.name,
                'start_time': datetime.combine(
                    self.today, self.client.reservation.start_time).strftime("%d.%m.%Y %H:%M"),
                'end_time': datetime.combine(
                    self.today, self.client.reservation.end_time).strftime("%d.%m.%Y %H:%M")
            }
        ]

        self.assertEqual(result, expected_output)
        os.remove("test_file.csv")
        print("test_write_to_csv", Reservation.list_of_reservations())

    def test_schedule(self):
        """Test of the schedule method of class Reservation and its ability to provide expected output."""

        date_start = self.today
        date_end = self.today
        param = 'print'
        expected_output = f"Today, {self.today.strftime('%d.%m.%Y')}\n* John Doe, from 10:00 to 11:00"
        stdout = sys.stdout
        captured_output = StringIO()
        sys.stdout = captured_output
        # Call the function that expects user input
        Reservation.schedule(date_start, date_end, param)
        captured_output.seek(0)
        output = captured_output.read()
        # Restore stdout
        sys.stdout = stdout
        # Compare output
        self.assertEqual(output.strip(), expected_output)


if __name__ == '__main__':
    unittest.main()
