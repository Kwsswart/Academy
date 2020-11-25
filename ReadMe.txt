# Classroom/Student Management System

This is student / class management system inspired to ease the workload of workers within a academic company, designed to allow them to control the progress and the classes/students within the academy.

## Permission levels

It is set up to deal with different levels of permissions: Master, Upper Management, Management, Teacher, Admin.
This is very aimed towards one type of academy and would require alot to adapt it to another type of company, however if required you may use this repository as a referance.




** Set-up

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

    
7) Once Done above run the following within the same flask shell in order to import all the pre-programming with for the class progress to work correctly.

    ```bash
    from import_file import looper
    looper('app/csv_files/1_hour', '1 Hour')
    looper('app/csv_files/1.5_hour', '1,5 Hours')
    looper('app/csv_files/2_hour', '2 Hours')
    looper('app/csv_files/2.5_hours', '2,5 Hours')
    ```

