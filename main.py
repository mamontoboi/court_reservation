from reservation import Client, Reservation
from datetime import datetime


class IncorrectDate(Exception):
    def __str__(self):
        return "Reservation needs to be made in {DD.MM.YYYY HH:MM} format"


def greeting():
    name = input("What's your Name?: \n").lower().title()
    if len(Client.list_of_client()) > 0:
        for client in Client.list_of_client():
            if client.name == 'name':
                print(f"Welcome back, {name}! \n")
    else:
        client = Client(name)
        print(f"Welcome, {name}!")

        return client


def menu(client):
    while True:
        choice = input("What do you want to do?\n\t"
                           "1. Make reservation\n\t"
                           "2. Cancel reservation\n\t"
                           "5. Exit\n")

        match choice:
            case '1':
                date_input = input(
                    "When would you like to book? {DD.MM.YYYY HH:MM}\n").replace('/', '.').replace('-', '.')
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
                date_input = input("What is the date of the reservation you want to cancel? {DD.MM.YYYY}\n")
                try:
                    reservation_date = datetime.strptime(date_input, "%d.%m.%y").date()
                except ValueError:
                    try:
                        reservation_date = datetime.strptime(date_input, "%d.%m.%Y").date()
                    except ValueError:
                        print("Please re-check your data. Cancellation date needs to be stated in DD.MM.YYYY format.")
                        continue
                client.cancel_reservation(reservation_date)

            case '5':
                print("Thank you for choosing our tennis club.")
                break

            case _:
                print("Please choose and action from menu")
                continue


if __name__ == '__main__':
    guest = greeting()
    menu(guest)
