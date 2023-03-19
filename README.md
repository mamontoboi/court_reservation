# Tennis Court Reservation Task
Created by Bogdan Bagdasaryan. 

## Usage

To run the unittests, navigate to the project directory and run `python -m unittest tests.py`.
To use the program, navigate to the project directory and run `python main.py`. 
No additional libraries need to be installed.

The program is easy to use. Reservation information is stored in RAM, so new reservations can be added while the program is running. 
The program processes reservations according to the following specification.


## Specification

Program should prompt user what to do.

What do you want to do:
1) Make a reservation
2) Cancel a reservation
3) Print schedule
4) Save schedule to a file
5) Exit

### 1. Make a reservation:
User should be prompted to give his full name, and date of a reservation
this should fail if:
* User has more than 2 reservations already this week
* Court is already reserved for the time user specified
* The date user gives is less than one hour from now

If the court is reserved the system should suggest the user to make a reservation on the closest possible time.


For example:

    $ Make a reservation 
    
    What's your Name?
    
    $ Jeff Spicoli
    
    When would you like to book? {DD.MM.YYYY HH:MM}
    
    $ 1.04.2023 15:00 
    
    The time you chose is unavailable, would you like to make a reservation for 16:00 instead? (yes/no)  # If the user chooses No, take them back to the previous step.
    
    $ Yes
    
    How long would you like to book court?  # Display possible periods in 30 minute intervals up to 90 minutes. If the court is reserved from 17:00 you should only show the first 2 options.
    1) 30 Minutes
    2) 60 Minutes
    3) 90 Minutes


### 2. Cancel a reservation:
User should be prompted to give his full name, and date of a reservation this should fail if:
* There is no reservation for this user on specified date
* The date user gives is less than one hour from now

### 3. Print schedule:
The user is prompted to enter a start and end date, then the schedule for the specified period is printed in the following format

    Today:
    * Name Surname start date - end date
    * Name Surname start date - end date
    
    Tomorrow:
    * Name Surname start date - end date
    
    Sunday:
    No Reservations

### 4. Save schedule to a file:
The user is prompted to enter the start date, end date, file format (csv or json) and file name, and then the schedule should be saved to a file in a format of the user's choice.
Examples are provided in this repository
 
 ## Notes

In the event of a failure, the user should be given a reason for the failure and be taken back to the menu.
