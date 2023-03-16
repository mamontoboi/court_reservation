from datetime import datetime, timedelta
import sqlite3


class Client:
    # _clients = []

    def __init__(self, name):
        self.name = name
        self.reservation = []
        # Client._clients.append(self)
        try:
            connection = sqlite3.connect('tennis_court_schedule.db')
            cursor = connection.cursor()

            sql_query_create_db = '''CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL);'''

            cursor.execute(sql_query_create_db)
            connection.commit()

            sql_query_insert = """INSERT INTO clients (name) VALUES (?);"""
            cursor.execute(sql_query_insert, self.name)
            connection.commit()
        except sqlite3.Error as e:
            print(f"The following problem was encountered: {e}.\n")
        finally:
            if connection:
                connection.close()

    @classmethod
    def list_of_client(cls):
        try:
            connection = sqlite3.connect('tennis_court_schedule.db')
            cursor = connection.cursor()

            sql_query_select = """SELECT * FROM clients;"""
            cursor.execute(sql_query_select)
            clients = cursor.fetchall()
            clients_list = []
            for element in clients:
                client = Client(element[0])
                clients_list.append(client)
            return clients_list
        except sqlite3.Error as e:
            print(f"The following problem was encountered: {e}.\n")
        finally:
            if connection:
                connection.close()
            print("The database was closed.\n")

    def _reservations_per_week(self, date):
        week_start = date - timedelta(days=date.weekday())
        week_end = week_start + timedelta(days=6)
        reservations_per_week = [reserv for reserv in self.reservation if week_start <= reserv.date <= week_end]
        if len(reservations_per_week) >= 2:
            return False
        else:
            return True

    def _next_available_time(self, date, time):
        global date_time_var
        global reservations_list
        for reservation in reservations_list:
            if reservation.date == date and reservation.start_time <= time < reservation.end_time:
                time = reservation.end_time
                if self._time_to_next_reservation(date, time) >= timedelta(minutes=30):
                    return time

    def _time_to_next_reservation(self, date, time):
        # date_time = datetime.combine(date, time)
        global date_time_var
        global reservations_list
        filter_reserv = [reservation for reservation in reservations_list
                         if datetime.combine(reservation.date, reservation.start_time) > date_time_var]
        if len(filter_reserv) > 0:
            timediff = min(datetime.combine(reservation.date, reservation.start_time) - date_time_var
                           for reservation in filter_reserv)
        else:
            timediff = timedelta(minutes=90)
        return timediff

    def _check_if_vacant(self, date, time):
        global reservations_list
        for item in reservations_list:
            if item.date == date and item.start_time <= time < item.end_time:
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

    def _create_new_reservation(self, date, time):
        available_time = self._time_to_next_reservation(date, time)
        print(available_time)
        if available_time == timedelta(minutes=90):
            choose_time = input('How long would you like to book court?\n'
                                '\t0. Cancel booking\n'
                                '\t1. 30 minutes\n'
                                '\t2. 60 minutes\n'
                                '\t3. 90 minutes\n')
        elif available_time == timedelta(minutes=60):
            choose_time = input('How long would you like to book court?\n'
                                '\t0. Cancel booking\n'
                                '\t1. 30 minutes\n'
                                '\t2. 60 minutes\n')
        else:
            choose_time = input('Would you like to book court for 30 minutes?\n'
                                '\t0. No\n'
                                '\t1. Yes\n')
        end_time = (datetime.combine(date, time) + timedelta(minutes=60)).time()
        match choose_time:
            case '1':
                end_time = (datetime.combine(date, time) + timedelta(minutes=30)).time()
            case '2':
                end_time = (datetime.combine(date, time) + timedelta(minutes=60)).time()
            case '3':
                end_time = (datetime.combine(date, time) + timedelta(minutes=90)).time()
            case '0':
                print("Booking process was cancelled")
                return False

        reservation = Reservation(date, time, end_time)
        self.reservation.append(reservation)
        date_str = datetime.strftime(date, "%d.%m.%Y")
        time_str = time.strftime("%H:%M")
        print(f"Reservation for {date_str} at {time_str} was added.")
        return True

    def make_reservation(self, date, time):
        global date_time_var
        date_time_var = datetime.combine(date, time)
        global reservations_list
        reservations_list = Reservation.list_of_reservations()
        if not self._reservations_per_week(date):
            print("Unfortunately, you already have 2 reservations that week.")
            return False

        if not self._check_if_not_past(date, time):
            print("This time has already passed. Try another time.")
            return False

        if not self._check_if_ample_time(date, time):
            print("Unfortunately, reservation cannot be made as less than 1 hours remained to the reservation time")
            return False

        if not self._check_if_vacant(date, time):
            print("Unfortunately, this time is already occupied.")
            next_available_time = self._next_available_time(date, time)
            choice = input(f"Would you like to make a reservation for {next_available_time.strftime('%H:%M')} "
                           f"instead? (yes/no)\n").lower()
            if choice == 'yes':
                self._create_new_reservation(date, time)
            else:
                print("Booking process was cancelled")
                return False
        else:
            self._create_new_reservation(date, time)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def cancel_reservation(self, date):
        for reservation in self.reservation:
            if reservation.date == date:
                if not self._check_if_ample_time(reservation.date, reservation.start_time):
                    print("Unfortunately, reservation cannot be cancelled as less than 1 hours "
                          "remained to the reservation time")
                    return

                self.reservation.remove(reservation)
                Reservation.list_of_reservations().remove(reservation)
                date_str = datetime.strftime(date, "%d.%m.%Y")
                print(f"Your reservation for {date_str} has been cancelled.")
                return

        print("You do not have a reservation for the specified date.")


class Reservation:
    # _reservations = []

    def __init__(self, client, date, start_time, end_time=None):
        self.client = client
        self.date = date
        self.start_time = start_time
        if end_time is None:
            self.end_time = (datetime.combine(date, start_time) + timedelta(minutes=60)).time()
        else:
            self.end_time = end_time

        # Reservation._reservations.append(self)
        try:
            connection = sqlite3.connect('tennis_court_schedule.db')
            cursor = connection.cursor()

            sql_query_create_db = '''CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client TEXT NOT NULL,
            FOREIGN KEY (client) REFERENCES clients(name),
            "date" DATE NOT NULL,
            start_time TIME NOT NULL,
            end_time TIME NOT NULL,
            );'''

            cursor.execute(sql_query_create_db)
            connection.commit()
            data_tuple = (self.client, self.date, self.start_time, self.end_time)
            sql_query_insert = """INSERT INTO reservations (client, "date", start_time, end_time) 
            VALUES (?, ?, ?, ?);"""
            cursor.execute(sql_query_insert, data_tuple)
            connection.commit()
        except sqlite3.Error as e:
            print(f"The following problem was encountered: {e}.\n")
        finally:
            if connection:
                connection.close()

    @classmethod
    def list_of_reservations(cls):
        return Reservation._reservations
