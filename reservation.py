"""This module provides classes and functions for managing reservations for tennis courts.

It includes the following classes:
- Client: A class representing a client who can make reservations for tennis courts.
- CustomEncoder: A custom JSON encoder that can serialize instances of the Client class.
- Reservation: A class representing a reservation made by a client for a specific date and time.
"""

import csv
from datetime import datetime, timedelta
import json
from json import JSONEncoder
import re


class CustomEncoder(JSONEncoder):
    """A custom JSON encoder that can serialize instances of the Client class.

    Instances of the Client class are serialized as strings containing their name attribute.
    All other values are serialized using the default serialization provided by
    the JSONEncoder base class.
    """

    def default(self, o):
        if isinstance(o, Client):
            return str(o.name)

        return super().default(o)


class Client:
    """A class representing a client who can make reservations for tennis courts.

    Attributes
    ----------
    name : str
        The name of the client.
    reservation : list
        A list of reservations made by the client.
    _clients : list
        A list of all clients.

    Methods
    -------
    list_of_client(cls)
        Returns a list of all clients.
    _reservations_per_week(self, date)
        Checks if the client has more than two reservations in a week.
    _next_available_time(self, date, time, all_reservations)
        Returns the next available time for the client to make a reservation.
    _time_to_next_reservation(self, date, time, all_reservations)
        Returns the time to the next reservation for the given date and time.
    _check_if_vacant(self, date, time, all_reservations)
        Checks if the court is vacant at the given date and time.
    _check_if_not_past(self, date, time)
        Checks if the given date and time has already passed.
    _check_if_ample_time(self, date, time)
        Checks if there is at least 1 hour remained to the given date and time.
    _create_new_reservation(self, date, time, all_reservations)
        Creates a new reservation for the given date and time.
    make_reservation(self, date, time)
        Enables the client to make a new reservation for the given date and time.
    cancel_reservation(self, date)
        Cancels a reservation for the specified date, if it exists.
    __str__()
        Returns a string representation of the client object.
    __repr__()
        Returns a string representation of the client object.
    """

    _clients = []

    def __init__(self, name):
        """Initializes a new instance of the Client class."""

        self.name = name
        self.reservation = []
        Client._clients.append(self)

    @classmethod
    def list_of_client(cls):
        """Returns a list of all clients."""

        return Client._clients

    def _reservations_per_week(self, date):
        """Checks if the client has more than two reservations in a week."""

        week_start = date - timedelta(days=date.weekday())
        week_end = week_start + timedelta(days=6)
        reservations_per_week = [reservation for reservation in self.reservation
                                 if week_start <= reservation.date <= week_end]
        if len(reservations_per_week) >= 2:
            return False
        return True

    def _next_available_time(self, date, time, all_reservations):
        """Returns the next available time for the client to make a reservation."""

        for reservation in all_reservations:
            if reservation.date == date and reservation.start_time <= time < reservation.end_time:
                time = reservation.end_time
                if self._time_to_next_reservation(date, time, all_reservations) >= timedelta(minutes=30):
                    return time
        return False

    def _time_to_next_reservation(self, date, time, all_reservations):
        """Returns the time to the next reservation for the given date and time."""

        date_time_var = datetime.combine(date, time)
        filter_reservations = [reservation for reservation in all_reservations
                               if datetime.combine(reservation.date, reservation.start_time) > date_time_var and
                               timedelta(minutes=0) < datetime.combine(reservation.date, reservation.start_time) -
                               date_time_var < timedelta(minutes=90)]
        if len(filter_reservations) > 0:
            timediff = min(datetime.combine(reservation.date, reservation.start_time) - date_time_var
                           for reservation in filter_reservations)
        else:
            timediff = timedelta(minutes=90)
        return timediff

    def _check_if_vacant(self, date, time, all_reservations):
        """Checks if the court is vacant at the given date and time."""

        for reservation in all_reservations:
            if reservation.date == date and reservation.start_time <= time < reservation.end_time:
                return False
        return True

    def _check_if_not_past(self, date, time):
        """Checks if the given date and time has already passed.
        Reservation fails if time has already passed
        """

        time_diff = (datetime.combine(date, time) - datetime.now()).total_seconds()
        if time_diff <= 0:
            return False
        return True

    def _check_if_ample_time(self, date, time):
        """Checks if there is at least 1 hour remained to the given date and time."""

        time_diff = (datetime.combine(date, time) - datetime.now()).total_seconds()
        if time_diff < 3600:
            return False
        return True

    def _create_new_reservation(self, date, time, all_reservations):
        """Creates a new reservation for the given date and time."""

        available_time = self._time_to_next_reservation(date, time, all_reservations)
        if available_time >= timedelta(minutes=90):
            choose_time = input('How long would you like to book the court?\n'
                                '\t0. Cancel booking\n'
                                '\t1. 30 minutes\n'
                                '\t2. 60 minutes\n'
                                '\t3. 90 minutes\n').strip()
        elif available_time == timedelta(minutes=60):
            choose_time = input('How long would you like to book the court?\n'
                                '\t0. Cancel booking\n'
                                '\t1. 30 minutes\n'
                                '\t2. 60 minutes\n').strip()
        else:
            choose_time = input('Would you like to book the court for 30 minutes?\n'
                                '\t0. No\n'
                                '\t1. Yes\n').lower().strip()
        end_time = (datetime.combine(date, time) + timedelta(minutes=60)).time()
        match choose_time:
            case '1' | '30' | 'yes':
                end_time = (datetime.combine(date, time) + timedelta(minutes=30)).time()
            case '2' | '60':
                end_time = (datetime.combine(date, time) + timedelta(minutes=60)).time()
            case '3' | '90':
                end_time = (datetime.combine(date, time) + timedelta(minutes=90)).time()
            case '0' | 'no':
                print("The booking process was cancelled.\n")
                return False

        reservation = Reservation(self, date, time, end_time)
        self.reservation.append(reservation)
        date_str = datetime.strftime(date, "%d.%m.%Y")
        time_str = time.strftime("%H:%M")
        minutes_dt = (datetime.combine(date, end_time) - datetime.combine(date, time))
        minutes = minutes_dt.total_seconds() / 60
        print(f"A reservation for {date_str} at {time_str} for {minutes:.0f} minutes has been added.\n")
        return True

    def make_reservation(self, date, time):
        """Enables the client to make a new reservation for the given date and time.

        Side effects:
            - If the client already has 2 reservations for the specified week,
              the method will return False and print a message indicating that
              the client already has 2 reservations for the week.

            - If the specified time has already passed, the method will return False
              and print a message indicating that the time has already passed.
.
            - If there is less than 1 hour remaining until the specified reservation time,
              the method will return False and print a message indicating that the reservation
              cannot be made due to insufficient time.

            - If the specified time is already occupied, the method will prompt the client
              to make a reservation for the next available time instead. If the client agrees,
              the method will create a reservation for the next available time. If the client
              declines, the method will return False and print a message indicating that
              the booking process was cancelled.

            - If the specified time is vacant and all other conditions are met,
              the method will create a new reservation and return True.
        """

        all_reservations = Reservation.list_of_reservations()
        if not self._reservations_per_week(date):
            print("Unfortunately, you already have 2 reservations that week.\n")
            return False

        if not self._check_if_not_past(date, time):
            print("This time has already passed. Please choose another time.\n")
            return False

        if not self._check_if_ample_time(date, time):
            print("Unfortunately, the reservation cannot be made "
                  "as there is less than 1 hour remaining until the reservation time.\n")
            return False

        if not self._check_if_vacant(date, time, all_reservations):
            print("Unfortunately, this time is already occupied.\n")
            next_available_time = self._next_available_time(date, time, all_reservations)
            while True:
                choice = input(f"Would you like to make a reservation for {next_available_time.strftime('%H:%M')} "
                               f"instead? (yes/no)\n").lower()
                if choice == 'yes':
                    self._create_new_reservation(date, next_available_time, all_reservations)
                    return True
                if choice == 'no':
                    print("The booking process was cancelled.\n")
                    return False
                continue

        self._create_new_reservation(date, time, all_reservations)
        return True

    def __str__(self):
        """Returns a string representation of the client."""

        return self.name

    def __repr__(self):
        """Returns a string representation of the client."""

        return self.name

    def cancel_reservation(self, date):
        """Cancels a reservation for the specified date, if it exists.

        Side effects:
            - If a reservation for the specified date exists, it is removed from the
              list of reservations associated with this customer, and from the global
              list of reservations.
            - If a reservation for the specified date does not exist, a message is printed
              to inform the user.
            - If the reservation cannot be cancelled because there is less than 1 hour
              remaining until the reservation time, a message is printed to inform the user.
        """

        for reservation in self.reservation:
            if reservation.date == date:
                if not self._check_if_ample_time(reservation.date, reservation.start_time):
                    print("Unfortunately, the reservation cannot be cancelled"
                          " as there is less than 1 hour remaining until the reservation time.\n")
                    return False
                self.reservation.remove(reservation)
                Reservation.list_of_reservations().remove(reservation)
                date_str = datetime.strftime(date, "%d.%m.%Y")
                print(f"Your reservation for {date_str} has been cancelled.\n")
                return True
        print("You do not have a reservation for the specified date.\n")


class Reservation:
    """Represents a reservation made by a client for a specific date and time.

    Attributes:
        client (str): The name of the client who made the reservation.
        date (datetime.date): The date of the reservation.
        start_time (datetime.time): The start time of the reservation.
        end_time (datetime.time): The end time of the reservation.
            If None is provided, end time is set to start time plus one hour.
        _reservations (list): A list of all reservations made, used for class-level operations.

    Methods:
        __init__(self, client, date, start_time, end_time)
            Initializes a new instance of the Reservation class.
        __str__(self)
            Returns a string representation of the reservation.
        __repr__(self)
            Returns a string representation of the reservation's dictionary.
        list_of_reservations(cls)
            Returns a list of all reservations made.
        _is_valid_file_name(file_name)
            Checks whether a given file name is valid (i.e. doesn't contain any forbidden symbols).
        _provide_file_name()
            Asks the user to provide a valid file name to save the schedule to.
        _serialize_to_json(data)
            Serializes the reservation data to a JSON file.
        _write_to_csv(data)
            Writes the reservation data to a CSV file.
        schedule(cls, date_start, date_end, param)
            Prints or saves the schedule for the given date range, in the specified format.
    """

    _reservations = []

    def __init__(self, client, date, start_time, end_time=None):
        """Initializes a new instance of the Reservation class."""

        self.client = client
        self.date = date
        self.start_time = start_time
        if end_time is None:
            self.end_time = (datetime.combine(date, start_time) + timedelta(minutes=60)).time()
        else:
            self.end_time = end_time
        Reservation._reservations.append(self)

    def __str__(self):
        """Returns a string representation of the reservation."""

        return f"Reservation made by {self.client} on {self.date} from {self.start_time} to {self.end_time}."

    def __repr__(self):
        """Returns a string representation of the reservation's dictionary."""

        return str(self.__dict__)

    @classmethod
    def list_of_reservations(cls):
        """Returns a list of all reservations made."""

        return Reservation._reservations

    @staticmethod
    def is_valid_file_name(file_name):
        """Checks whether a given file name is valid (i.e. doesn't contain any forbidden symbols)."""

        forbidden_symbols = r'[<>:\\"/|?*\x00-\x1f]'
        if not re.search(forbidden_symbols, file_name):
            return True
        print("Special characters such as <, >, :, \\, /, *, |, ?, \" or tab are not allowed in file names.\n")
        return False

    @staticmethod
    def provide_file_name():
        """Asks the user to provide a valid file name to save the schedule to."""

        while True:
            file_name = input("Please enter a valid file name to save the schedule.\n").strip()
            if Reservation.is_valid_file_name(file_name):
                return file_name
            continue

    @staticmethod
    def serialize_to_json(data):
        """Serializes the reservation data to a JSON file."""

        file_name = Reservation.provide_file_name()
        result = {}
        for date, reservations in data.items():
            date_str = date.strftime("%d.%m")
            result[date_str] = []
            # Checks if reservations were made that date
            if len(reservations) > 0:
                for element in reservations:
                    details = {"name": element[0], "start_time": element[1].strftime("%H:%M"),
                               "end_time": element[2].strftime("%H:%M")}
                    result[date_str].append(details)

        # Dumps dictionary into json file
        with open(f"{file_name}.json", 'w', encoding='utf-8') as json_file:
            json.dump(result, json_file, indent=2, cls=CustomEncoder)
        print(f"The schedule has been saved in {file_name}.json file.\n")

    @staticmethod
    def write_to_csv(data):
        """Writes the reservation data to a CSV file."""

        file_name = Reservation.provide_file_name()
        with open(f"{file_name}.csv", 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=['name', 'start_time', 'end_time'],
                quoting=csv.QUOTE_NONE
            )

            writer.writeheader()
            for date, reservations in data.items():
                for record in reservations:
                    print(record[1], record[2])
                    writer.writerow({
                        'name': record[0],
                        'start_time': datetime.combine(date, record[1]).strftime("%d.%m.%Y %H:%M"),
                        'end_time': datetime.combine(date, record[2]).strftime("%d.%m.%Y %H:%M")
                    })
        print(f"The schedule has been saved in {file_name}.csv file.\n")

    @classmethod
    def schedule(cls, date_start, date_end, param):
        """Prints or saves the schedule for the given date range, in the specified format."""

        def _get_day_name(target_date):
            """Converts the datetime object into current date related aliases."""
            today = date.today()
            tomorrow = today + timedelta(days=1)
            after_tomorrow = today + timedelta(days=2)
            yesterday = today - timedelta(days=1)
            before_yesterday = today - timedelta(days=2)
            if target_date == today:
                return "Today"
            if target_date == tomorrow:
                return "Tomorrow"
            if target_date == after_tomorrow:
                return "The day after tomorrow"
            if target_date == yesterday:
                return "Yesterday"
            if target_date == before_yesterday:
                return "The day before yesterday"

            return target_date.strftime("%A")

        all_reservations = Reservation.list_of_reservations()
        # Creates the dictionary with all days in the given range
        period_schedule = {}
        for day in range((date_end - date_start).days + 1):
            current_date = date_start + timedelta(days=day)
            period_schedule[current_date] = []

        # Adds a reservation object to the dictionary, where each key corresponds
        # to a date on which the reservation is made.
        for reservation in all_reservations:
            if date_start <= reservation.date <= date_end:
                period_schedule.get(reservation.date).append((reservation.client,
                                                              reservation.start_time, reservation.end_time))

        # Sorts all the reservations for each day in a period by the time the reservation starts
        for date, reservation in period_schedule.items():
            period_schedule[date] = sorted(reservation, key=lambda details: details[1])

        if param == 'print':
            for date, reservations in period_schedule.items():
                print(f"\n{_get_day_name(date)}, {datetime.strftime(date, '%d.%m.%Y')}")
                if len(reservations) > 0:
                    for reservation in reservations:
                        print(f"* {reservation[0]}, from "
                              f"{reservation[1].strftime('%H:%M')} "
                              f"to {reservation[2].strftime('%H:%M')}")
                else:
                    print("No Reservations")
            print()
        elif param == 'json':
            Reservation.serialize_to_json(period_schedule)

        else:
            Reservation.write_to_csv(period_schedule)
