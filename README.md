## Library-Service-Api
API allows authenticated users to create online borrowings in library

## Features
1. JWT Authenticated
2. Admin panel (/admin/)
3. Documentation (located at /api/doc/swagger/)
4. Telegram bot to get information about borrowing
5. Daily notifications of overdue borrowings
## Installation
Python3 must be already installed

```python
git clone https://github.com/andy77andy/Library-Service-Api
cd airlines
pythone -m venv venv 
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
celery -A library_service worker -l info --pool=solo

```
## Getting access

```python
create new user via /api/user/register/
get access token via /api/user/token/
get link to start telegram bot /api/telegram_notifications/start/
```

In this project uses environment variables for configuration, it stores sensitive data and configuration variables that are necessary for the project.
The .env.sample file provided as an example for the .env file, it includes necessary variables.

To configure the project:

Locate the .env.sample file in the project's root directory.
Duplicate the .env.sample file and rename the duplicated file to .env.
Open the .env file and replace the placeholder values with the actual configuration values specific to your setup.
Remember to keep the .env file secure and avoid sharing it publicly or committing it to version control systems.
