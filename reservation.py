import csv
from datetime import datetime, timedelta
import json
from json import JSONEncoder


class CustomEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Client):
            return str(obj.name)


class Client:
    _clients = []

    def __init__(self, name):
        self.name = name
        self.reservation = []
        Client._clients.append(self)

    @classmethod
    def list_of_client(cls):
        return Client._clients

    def _reservations_per_week(self, date):
        week_start = date - timedelta(days=date.weekday())
        week_end = week_start + timedelta(days=6)
        reservations_per_week = [reservation for reservation in self.reservation
                                 if week_start <= reservation.date <= week_end]
        if len(reservations_per_week) >= 2:
            return False

        return True

    def _next_available_time(self, date, time, all_reservations):
        for reservation in all_reservations:
            if reservation.date == date and reservation.start_time <= time < reservation.end_time:
                time = reservation.end_time
                if self._time_to_next_reservation(date, time, all_reservations) >= timedelta(minutes=30):
                    return time
        return False

    def _time_to_next_reservation(self, date, time, all_reservations):
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
        for reservation in all_reservations:
            if reservation.date == date and reservation.start_time <= time < reservation.end_time:
                return False
        return True

    def _check_if_not_past(self, date, time):
        time_diff = (datetime.combine(date, time) - datetime.now()).total_seconds()
        if time_diff <= 0:
            return False
        return True

    def _check_if_ample_time(self, date, time):
        time_diff = (datetime.combine(date, time) - datetime.now()).total_seconds()
        if time_diff < 3600:
            return False
        return True

    def _create_new_reservation(self, date, time, all_reservations):
        available_time = self._time_to_next_reservation(date, time, all_reservations)
        if available_time >= timedelta(minutes=90):
            choose_time = input('How long would you like to book court?\n'
                                '\t0. Cancel booking\n'
                                '\t1. 30 minutes\n'
                                '\t2. 60 minutes\n'
                                '\t3. 90 minutes\n').strip()
        elif available_time == timedelta(minutes=60):
            choose_time = input('How long would you like to book court?\n'
                                '\t0. Cancel booking\n'
                                '\t1. 30 minutes\n'
                                '\t2. 60 minutes\n').strip()
        else:
            choose_time = input('Would you like to book court for 30 minutes?\n'
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
                print("Booking process was cancelled.\n")
                return False

        reservation = Reservation(self, date, time, end_time)
        self.reservation.append(reservation)
        date_str = datetime.strftime(date, "%d.%m.%Y")
        time_str = time.strftime("%H:%M")
        minutes_dt = (datetime.combine(date, end_time) - datetime.combine(date, time))
        minutes = minutes_dt.total_seconds() / 60
        print(f"Reservation for {date_str} at {time_str} for {minutes:.0f} minutes was added.\n")
        return True

    def make_reservation(self, date, time):
        all_reservations = Reservation.list_of_reservations()
        if not self._reservations_per_week(date):
            print("Unfortunately, you already have 2 reservations that week.\n")
            return False

        if not self._check_if_not_past(date, time):
            print("This time has already passed. Try another time.\n")
            return False

        if not self._check_if_ample_time(date, time):
            print("Unfortunately, reservation cannot be made as less than 1 hours remained to the reservation time.\n")
            return False

        if not self._check_if_vacant(date, time, all_reservations):
            print("Unfortunately, this time is already occupied.\n")
            next_available_time = self._next_available_time(date, time, all_reservations)
            choice = input(f"Would you like to make a reservation for {next_available_time.strftime('%H:%M')} "
                           f"instead? (yes/no)\n").lower()
            if choice == 'yes':
                self._create_new_reservation(date, next_available_time, all_reservations)
                return True
            print("Booking process was cancelled.\n")
            return False

        self._create_new_reservation(date, time, all_reservations)
        return True

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def cancel_reservation(self, date):
        for reservation in self.reservation:
            if reservation.date == date:
                if not self._check_if_ample_time(reservation.date, reservation.start_time):
                    print("Unfortunately, reservation cannot be cancelled as less than 1 hours "
                          "remained to the reservation time.\n")
                    return

                self.reservation.remove(reservation)
                Reservation.list_of_reservations().remove(reservation)
                date_str = datetime.strftime(date, "%d.%m.%Y")
                print(f"Your reservation for {date_str} has been cancelled.\n")
                return

        print("You do not have a reservation for the specified date.\n")


class Reservation:
    _reservations = []

    def __init__(self, client, date, start_time, end_time=None):
        self.client = client
        self.date = date
        self.start_time = start_time
        if end_time is None:
            self.end_time = (datetime.combine(date, start_time) + timedelta(minutes=60)).time()
        else:
            self.end_time = end_time
        Reservation._reservations.append(self)

    def __str__(self):
        return f"Reservation by {self.client} on {self.date} from {self.start_time} until {self.end_time}"

    def __repr__(self):
        return str(self.__dict__)

    @classmethod
    def list_of_reservations(cls):
        return Reservation._reservations

    @staticmethod
    def _serialize_to_json(data, date_start, date_end):
        data_start_str = datetime.strftime(date_start, "%d.%m")
        data_end_str = datetime.strftime(date_end, "%d.%m")
        result = {}
        for date, reservations in data.items():
            date_str = date.strftime("%d.%m")
            result[date_str] = []
            if len(reservations) > 0:
                for element in reservations:
                    details = {"name": element[0], "start_time": element[1].strftime("%H:%M"),
                               "end_time": element[2].strftime("%H:%M")}
                    result[date_str].append(details)

        with open(f"{data_start_str}-{data_end_str}.json", 'w') as json_file:
            json.dump(result, json_file, indent=2, cls=CustomEncoder)
        print(f"The schedule was saved in {data_start_str}-{data_end_str}.json file.\n")

    @staticmethod
    def _write_to_csv(data, date_start, date_end):
        data_start_str = datetime.strftime(date_start, "%d.%m")
        data_end_str = datetime.strftime(date_end, "%d.%m")
        with open(f"{data_start_str}-{data_end_str}.csv", 'w', newline='') as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=['name', 'start_time', 'end_time'],
                quoting=csv.QUOTE_NONE
            )

            writer.writeheader()
            for date, reservations in data.items():
                for record in reservations:
                    writer.writerow({
                        'name': record[0],
                        'start_time': datetime.combine(date, record[1]).strftime("%d.%m.%Y %H:%M"),
                        'end_time': datetime.combine(date, record[2]).strftime("%d.%m.%Y %H:%M")
                    })
        print(f"The schedule was saved in {data_start_str}-{data_end_str}.csv file.\n")

    @classmethod
    def schedule(cls, date_start, date_end, param):

        def _get_day_name(target_date):
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
        period_schedule = {}
        for day in range((date_end - date_start).days + 1):
            current_date = date_start + timedelta(days=day)
            period_schedule[current_date] = []

        for reservation in all_reservations:
            if date_start <= reservation.date <= date_end:
                period_schedule.get(reservation.date).append((reservation.client,
                                                              reservation.start_time, reservation.end_time))
        for date, reservation in period_schedule.items():
            period_schedule[date] = sorted(reservation, key=lambda details: details[1])

        if param == 'print':
            for date, reservations in period_schedule.items():
                print(f"\n{_get_day_name(date)}, {datetime.strftime(date, '%d.%m.%Y')}")
                if len(reservations) > 0:
                    for reservation in reservations:
                        print(f"* {reservation[0]}, from "
                              f"{reservation[1].strftime('%H:%M')} "
                              f"till {reservation[2].strftime('%H:%M')}")
                else:
                    print("No Reservations")
            print()
        elif param == 'json':
            Reservation._serialize_to_json(period_schedule, date_start, date_end)

        else:
            Reservation._write_to_csv(period_schedule, date_start, date_end)
