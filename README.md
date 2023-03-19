The court_reservation project was created by Bogdan Bagdasaryan. 
To run the unittests, navigate to the project directory and run `python -m unittest tests.py`.
To use the program, navigate to the project directory and run `python main.py`. 
No additional libraries need to be installed.

The program is easy to use. Reservation information is stored in RAM, so new reservations can be added while the program is running. 
The program processes reservations according to the following task requirements:

1. Make a reservation:
User should be prompted to give his full name, and date of a reservation this should fail if:

- User has more than 2 reservations already this week
- Court is already reserved for the time user specified
- The date user gives is less than one hour from now

If the court is reserved the system should suggest the user to make a reservation on the closest possible time.

2. Cancel a reservation:
User should be prompted to give his full name, and date of a reservation this should fail if:

- There is no reservation for this user on specified date
- The date user gives is less than one hour from now

3. Print schedule:
The user is prompted to enter a start and end date, then the schedule for the specified period is printed.

4. Save schedule to a file:
The user is prompted to enter the start date, end date, file format (csv or json) and file name, and then the schedule should be saved to a file in a format of the user's choice.
