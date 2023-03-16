from reservation import Client, Reservation
from datetime import datetime


def main():
    while True:
        choice = input("Press 1 to start the process of reservation\nPress 2 for exit\n")
        match choice:
            case '1':
                guest = greeting()
                menu(guest)
            case '2':
                break
            case _:
                continue


def greeting():

    def valid_name(client_name):
        if all(char.isalpha() or char.isspace() for char in client_name) and len(client_name.split()) == 2:
            return True
        print("Write both your name and your surname, please.")
        return False

    while True:
        name = input("What's your name and surname?: \n").lower().strip().title()
        if valid_name(name):
            clients = Client.list_of_client()
            if len(clients) > 0:
                for client in clients:
                    if client.name == name:
                        print(f"Welcome back, {name}! \n")
                        return client

                client = Client(name)
                print(f"Welcome, {name}!")
                return client

            else:
                client = Client(name)
                print(f"Welcome, {name}!")

                return client


def menu(client):
    while True:
        choice = input("What do you want to do?\n\t"
                       "1. Make reservation\n\t"
                       "2. Cancel reservation\n\t"
                       "3. Print schedule\n\t"
                       "5. Exit\n")

        match choice:
            case '1':
                date_input = input(
                    "When would you like to book? {DD.MM.YYYY HH:MM}\n").replace('/', '.').replace('-', '.').strip()
                try:
                    reservation_datetime = datetime.strptime(date_input, "%d.%m.%y %H:%M")
                except ValueError:
                    try:
                        reservation_datetime = datetime.strptime(date_input, "%d.%m.%Y %H:%M")
                    except ValueError:
                        print("Please re-check your data. Reservation needs to be made in DD.MM.YYYY HH:MM format.")
                        continue
                date = reservation_datetime.date()
                time = reservation_datetime.time()
                if not client.make_reservation(date, time):
                    continue

            case '2':
                date_input = input("What is the date of the reservation "
                                   "you want to cancel? {DD.MM.YYYY}\n").replace('/', '.').replace('-', '.').strip()
                try:
                    reservation_date = datetime.strptime(date_input, "%d.%m.%y").date()
                except ValueError:
                    try:
                        reservation_date = datetime.strptime(date_input, "%d.%m.%Y").date()
                    except ValueError:
                        print("Please re-check your data. "
                              "Cancellation date needs to be stated in DD.MM.YYYY format.")
                        continue
                client.cancel_reservation(reservation_date)

            case '3':
                date_from = input("From what date? {DD.MM.YYYY}\n").replace('/', '.').replace('-', '.').strip()
                date_to = input("Until what date? {DD.MM.YYYY}\n").replace('/', '.').replace('-', '.').strip()
                try:
                    date_from_dt = datetime.strptime(date_from, "%d.%m.%y").date()
                    date_to_dt = datetime.strptime(date_to, "%d.%m.%y").date()
                except ValueError:
                    try:
                        date_from_dt = datetime.strptime(date_from, "%d.%m.%Y").date()
                        date_to_dt = datetime.strptime(date_to, "%d.%m.%Y").date()
                    except ValueError:
                        print("Please write the data in DD.MM.YYYY format.")
                        continue
                Reservation.print_schedule(date_from_dt, date_to_dt)

            case '5':
                print("Thank you for choosing our tennis club.")
                break

            case _:
                print("Please choose and action from menu")
                continue


if __name__ == '__main__':
    main()
