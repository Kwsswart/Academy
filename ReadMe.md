# Classroom/Student Management System


This is student / class management system inspired to ease the workload of workers within a academic company, designed to allow them to control the progress and the classes/students within the academy.


## Permission levels


It is set up to deal with different levels of permissions: Master, Upper Management, Management, Teacher, Admin.
This is very aimed towards one type of academy and would require alot to adapt it to another type of company, however if required you may use this repository as a referance.


## Set-up


1) Ensure there is the directory


    ```
    app/static/uploads/avatars
    ```


2) Set the following variables in environment:


    ```python
    FLASK_APP = academy.py
    MAIL_SERVER=smtp.googlemail.com
    MAIL_PORT=587
    MAIL_USE_TLS=1
    MAIL_USERNAME=<Your-Email-Username>
    MAIL_PASSWORD=<Your-email-password>
    ADMINS=['admin@example.com']
    SECRET_KEY=you_will_never_guess
    ```


3) Install all libraries required:


    ```bash
    pip install -r requirements.txt
    ```


4) Set-up the database: 


    ```bash
    flask db upgrade
    ```


5) Once all above done open the flask shell:


    ```bash
    flask shell
    ```

6) Follow the steps in the Documentation.txt to set-up the database within the flask shell.


### 7) Before doing 7 ensure that the csv files follow the following pattern:


HOUR,LESSON NUMBER,NEW WORK TO,LAST WORD,EXERCISE<br>
1,1,16,Numbers,Alphabet and vowel sounds p10


**HOUR:** Must contain integers starting from 1 up.<br>
**LESSON** Must contain integers and follows the lesson numbers in whichever book you are using.<br>
**"NEW WORK TO"** Must contain integers and refers to the last page that you should get to.


#### These are very important to follow  for the application to function as expected.


8) Once Done above run the following within the same flask shell in order to import all the pre-programming with for the class progress to work correctly. Bare in mind this is an example and I have left the csv files within to allow for observation and work with to edit as needed


    ```bash
    from import_file import looper
    looper('app/csv_files/1_hour', '1 Hour')
    looper('app/csv_files/1.5_hour', '1,5 Hours')
    looper('app/csv_files/2_hour', '2 Hours')
    looper('app/csv_files/2.5_hours', '2,5 Hours')
    ```


#### The looper and importer will take a path as first argument and a 'time' as I have chosen to limit my groups as such, while the importer will take the file name and use that for the input.