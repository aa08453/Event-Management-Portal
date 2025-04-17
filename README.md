# Event Management Portal

A Django web application for managing and organizing events, with role-based access for students and event managers.

## Project Structure

```
event_management_portal/
│
├── events/                  # Main Django app
│   ├── __pycache__/         # Python cache
│   ├── migrations/          # Database migration files
│   ├── admin.py             # Django admin config
│   ├── apps.py              # App configuration
│   ├── forms.py             # Django forms
│   ├── models.py            # Data models: UserProfile, Event, etc.
│   ├── tests.py             # Unit tests
│   ├── urls.py              # App-level URL routing
│   └── views.py             # View logic
│
├── static/                  # Static files
│   ├── css/                 # Custom stylesheets
│   └── images/              # Image assets
│
├── templates/               # HTML templates
│
├── .gitignore               # Git ignored files
├── initialize_db.py         # Script to setup initial data (run this before migrations!)
├── manage.py                # Django management script
├── requirements.txt         # Python dependencies
```

---

## Setup Instructions

### Clone the Repository

```bash
git clone https://github.com/your-username/event_management_portal.git
cd event_management_portal
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Project Initialization

### Initialize the Database

Before applying migrations, run the custom database setup script:

```bash
python initialize_db.py
```

This script might create required groups, permissions, or default users.

### Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Run the Development Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser to access the portal.

---

## User Roles

- **Student**: Can view and register for published events.
- **Event Manager**: Can create, edit, publish, and manage their own events.

---

## Features

- Role-based access using `UserProfile`
- Event creation and ticket management
- Venue clash detection (2-hour buffer logic)
- Templates and static files organized for easy UI customization

---

## Requirements

See [`requirements.txt`](./requirements.txt) for full dependency list. 

