"# Library-Service-Api" 

This API provides functionality for online borrowings in library for users

Features:
    JWT Authenticated
    Admin panel 
    Documentation is located at /api/doc/swagger/
    Filter borrowings by user(for admin) & if they are active or not
    Using Telegram bot to get information about borrowing(new borrowings notifications for users, and overdue borrowings for admin )


Configuration:
    git clone https://github
    cd library-service
    py -m venv venv
    venv\Scripts\activate (on Windows)
    source venv/bin/activate (on macOS)
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py runserver
    celery -A library_service worker -l info --pool=solo


You can use the following test credentials:
Test superuser:
Email: admin@admin.com
Password: a1a2a3a4
Configuration variables:
The project uses environment variables for configuration. Please follow these steps to set up the required configuration files.

The .env file is used to store sensitive information and configuration variables that are necessary for the project to function properly.

The .env.sample file serves as a template or example for the .env file. It includes the necessary variables and their expected format, but with placeholder values.

To configure the project:

Locate the .env.sample file in the project's root directory.
Duplicate the .env.sample file and rename the duplicated file to .env.
Open the .env file and replace the placeholder values with the actual configuration values specific to your setup.
Remember to keep the .env file secure and avoid sharing it publicly or committing it to version control systems.
