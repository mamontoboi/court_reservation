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
                print("See you again soon.")
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


def date_valid(date):
    try:
        date_dt = datetime.strptime(date, "%d.%m.%y").date()
        return date_dt
    except ValueError:
        try:
            date_dt = datetime.strptime(date, "%d.%m.%Y").date()
            return date_dt
        except ValueError:
            print("Please re-check your data. "
                  "Date needs to be stated in DD.MM.YYYY format.")
            return False


def menu(client):
    while True:
        choice = input("What do you want to do?\n\t"
                       "1. Make reservation\n\t"
                       "2. Cancel reservation\n\t"
                       "3. Print schedule\n\t"
                       "4. Save schedule to a file\n\t"
                       "5. Exit\n").strip()

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
                if date_valid(date_input):
                    client.cancel_reservation(date_valid(date_input))
                else:
                    continue

            case '3':
                date_from = input("From what date? {DD.MM.YYYY}\n").replace('/', '.').replace('-', '.').strip()
                if date_valid(date_from):
                    date_from_dt = date_valid(date_from)
                else:
                    continue
                date_to = input("Until what date? {DD.MM.YYYY}\n").replace('/', '.').replace('-', '.').strip()
                if date_valid(date_to):
                    date_to_dt = date_valid(date_to)
                else:
                    continue
                Reservation.schedule(date_from_dt, date_to_dt, 'print')

            case '4':
                date_from = input("From what date? {DD.MM.YYYY}\n").replace('/', '.').replace('-', '.').strip()
                if date_valid(date_from):
                    date_from_dt = date_valid(date_from)
                else:
                    continue
                date_to = input("Until what date? {DD.MM.YYYY}\n").replace('/', '.').replace('-', '.').strip()
                if date_valid(date_to):
                    date_to_dt = date_valid(date_to)
                else:
                    continue
                file_format = input("\tPress 1 to save in json format\n\tPress 2 to save in csv format\n")
                match file_format:
                    case '1':
                        Reservation.schedule(date_from_dt, date_to_dt, 'json')

                    case '2':
                        Reservation.schedule(date_from_dt, date_to_dt, 'csv')

            case '5':
                print("Thank you for choosing our tennis club.\n")
                break

            case _:
                print("Please choose and action from menu")
                continue


if __name__ == '__main__':
    main()
