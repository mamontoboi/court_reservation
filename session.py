"""This module provides a user interface for a tennis club reservation system.

The only class in this module is Session, which represents the user interface.
The Session class provides methods to greet the user, display a main menu, make a reservation,
print the club's schedule, and save the schedule to a file.

This module requires the datetime module for date and time handling,
and the reservation module for the Client and Reservation classes.
"""

from datetime import datetime
from reservation import Client, Reservation


class Session:
    """Represents a tennis club user interface.

    Methods
    -------
    main(self)
        Runs the main session loop until session in completed by user.
    greeting(self)
        Greets the user and gets their name to retrieve or create an instance of class Client.
    _valid_name(self, client_name)
        Check if the name, provided by user, is valid.
    _menu(self, client)
        Displays a main menu of options to the user. Runs the selected option.
    _session_make_reservation(self, client)
        Prompts the user for a date and time to make the reservation.
    _print_schedule(self)
        Prompts the user for dates to print the club's schedule.
    _date_valid(self, date)
        Validates a date entered by the user and returns a datetime object if valid.
    _choose_dates(self)
        Prompts the user for two dates and returns them as datetime objects.
    _save_to_file(self)
        Prompts the user for dates and a file format, then saves the club's schedule to a file.
    """

    # def __init__(self):
    #     """Initializes a new instance of the Reservation class."""
    #
    #     self.main()

    def main(self):
        """Runs the main session loop until session in completed by user."""

        while True:
            choice = input("Press 1 to start the reservation process.\nPress 2 to exit.\n")
            match choice:
                case '1':
                    guest = self.greeting()
                    self.menu(guest)
                case '2':
                    print("Goodbye. See you again soon.")
                    break
                case _:
                    continue

    def _valid_name(self, client_name):
        """Check if the name, provided by user, is valid."""

        if all(char.isalpha() or char.isspace() for char in client_name) and len(client_name.split()) == 2:
            return True
        print("Please write your name and surname.")
        return False

    def greeting(self):
        """Greets the user and gets their name to retrieve or create an instance of class Client."""

        while True:
            name = input("What is your name and surname?\n").lower().strip().title()
            if self._valid_name(name):
                clients = Client.list_of_client()

                # Returns an existing client. Otherwise, creates a new client object.
                if len(clients) > 0:
                    for client in clients:
                        if client.name == name:
                            print(f"Welcome back, {name}!")
                            return client

                    client = Client(name)
                    print(f"Welcome, {name}!")
                    return client

                client = Client(name)
                print(f"Welcome, {name}!")

                return client

    def menu(self, client):
        """Displays a main menu of options to the user. Runs the selected option."""

        while True:
            choice = input("What do you want to do?\n\t"
                           "1. Make reservation\n\t"
                           "2. Cancel reservation\n\t"
                           "3. Print schedule\n\t"
                           "4. Save schedule to a file\n\t"
                           "5. Exit\n").strip()

            match choice:
                case '1':
                    if not self._session_make_reservation(client):
                        continue

                case '2':
                    date_input = input("What is the date of the reservation you want to cancel? "
                                       "{DD.MM.YYYY}\n").replace('/', '.').replace('-', '.').strip()
                    if self._date_valid(date_input):
                        client.cancel_reservation(self._date_valid(date_input))
                    else:
                        continue

                case '3':
                    if not self._print_schedule():
                        continue

                case '4':
                    if not self._save_to_file():
                        continue

                case '5':
                    print("Thank you for choosing our tennis club.\n")
                    break

                case _:
                    print("Please choose an action from the menu.")
                    continue

    def _session_make_reservation(self, client):
        """Prompts the user for a date and time to make the reservation."""

        date_input = input(
            "When would you like to book? {DD.MM.YYYY HH:MM}\n").replace('/', '.').replace('-', '.').strip()
        try:
            reservation_datetime = datetime.strptime(date_input, "%d.%m.%y %H:%M")
        except ValueError:
            try:
                reservation_datetime = datetime.strptime(date_input, "%d.%m.%Y %H:%M")
            except ValueError:
                print("Please check the format of your date and time. "
                      "Reservations must be made in DD.MM.YYYY HH:MM format.")
                return False
        date = reservation_datetime.date()
        time = reservation_datetime.time()
        if not client.make_reservation(date, time):
            return False
        return True

    def _print_schedule(self):
        """Prompts the user for dates to print the club's schedule."""

        dates = self._choose_dates()
        date_from_dt = dates[0]
        date_to_dt = dates[1]
        Reservation.schedule(date_from_dt, date_to_dt, 'print')
        return True

    def _date_valid(self, date):
        """Validates a date entered by the user and returns a datetime object if valid."""

        try:
            date_dt = datetime.strptime(date, "%d.%m.%y").date()
            return date_dt
        except ValueError:
            try:
                date_dt = datetime.strptime(date, "%d.%m.%Y").date()
                return date_dt
            except ValueError:
                print("Please check the format of your date and time. "
                      "Reservations must be made in DD.MM.YYYY format.")
                return False

    def _choose_dates(self):
        """Prompts the user for two dates and returns them as datetime objects."""

        while True:
            date_from = input("From what date would you like to save the schedule? "
                              "{DD.MM.YYYY}\n").replace('/', '.').replace('-', '.').strip()
            if self._date_valid(date_from):
                date_from_dt = self._date_valid(date_from)
                break
            continue
        while True:
            date_to = input("Until what date would you like to save the schedule? "
                            "{DD.MM.YYYY}\n").replace('/', '.').replace('-', '.').strip()
            if self._date_valid(date_to):
                date_to_dt = self._date_valid(date_to)
                break
            continue
        return date_from_dt, date_to_dt

    def _save_to_file(self):
        """Prompts the user for dates and a file format, then saves the club's schedule to a file."""

        dates = self._choose_dates()
        date_from_dt = dates[0]
        date_to_dt = dates[1]
        while True:
            file_format = input("\tPress 1 to save in JSON format\n\tPress 2 to save in CSV format\n"
                                "\tPress 3 to cancel saving\n")
            if file_format == '1':
                Reservation.schedule(date_from_dt, date_to_dt, 'json')
                break
            if file_format == '2':
                Reservation.schedule(date_from_dt, date_to_dt, 'csv')
                break
            if file_format == '3':
                break
            continue
