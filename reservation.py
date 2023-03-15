from datetime import datetime, timedelta


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
                pass
        else:
            available_time = self._time_to_next_reservation(date, time)
            print(available_time)
            reservation = Reservation(date, time)
            # reservation = Reservation(date, time, time + timedelta(minutes=length))
            self.reservation.append(reservation)
            date_str = datetime.strftime(date, "%d.%m.%Y")
            time_str = time.strftime("%H:%M")
            print(f"Reservation for {date_str} at {time_str} was added.")
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
                          "remained to the reservation time")
                    return

                self.reservation.remove(reservation)
                Reservation.list_of_reservations().remove(reservation)
                date_str = datetime.strftime(date, "%d.%m.%Y")
                print(f"Your reservation for {date_str} has been cancelled.")
                return

        print("You do not have a reservation for the specified date.")


class Reservation:
    _reservations = []

    def __init__(self, date, start_time, end_time=None):
        self.date = date
        self.start_time = start_time
        if end_time is None:
            self.end_time = (datetime.combine(date, start_time) + timedelta(minutes=60)).time()
        else:
            self.end_time = end_time
        Reservation._reservations.append(self)

    @classmethod
    def list_of_reservations(cls):
        return Reservation._reservations



