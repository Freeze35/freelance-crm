# Client Form Testing

This section documents the settings,view,forms,urls and models inside clients

## Settings
## Environment Variables
The system requires a `.env` file in the root directory. Below are the key variables:

| Variable | Description | Default |
| :--- | :--- | :--- |
| `DEBUG` | Enable/Disable debug mode | `False` |
| `SECRET_KEY` | Django secret key for security | (Fallback used) |
| `DATABASE_URL` | Connection string for the database | `sqlite:///...` |
| `REDIS_URL` | Connection string for Celery broker | `redis://...` |
| `TELEGRAM_BOT_TOKEN` | Token from @BotFather | `""` |

## Core Components

### 1. Installed Applications
The project is built using a modular approach. Core apps:
* **Internal**: `clients`, `projects`, `tasks`, `invoices`.
* **Third-party**: `crispy_forms` (Tailwind), `django_htmx`.

### 2. Database Strategy
The system automatically switches databases based on the environment:
* **Production/Dev**: Uses the `DATABASE_URL` provided in environment.
* **Testing**: Uses an **In-memory SQLite** database for maximum performance during `pytest` runs.

### 3. Background Tasks (Celery)
Automated notifications are scheduled via **Celery Beat**. 
- **Task**: `tasks.tasks.send_telegram_notifications`
- **Morning Schedule**: 09:00 (Europe/Moscow)
- **Evening Schedule**: 18:00 (Europe/Moscow)

::: crm.settings
    options:
      show_root_heading: false
      show_source: true

## Forms
::: crm.forms
    options:
          show_root_heading: true
          show_source: true
          members_order: source

## Views
::: crm.views
    options:
      show_root_heading: true
      show_source: true
      members_order: source

## Endpoint Overview

| Base URL Path | Namespace | Description | Component |
| :--- | :--- | :--- | :--- |
| `/` | `dashboard` | Main Analytics Dashboard | Core View |
| `/admin/` | `admin` | Django Administration Panel | System Admin |
| `/projects/` | `projects` | Project & Budget Management | Projects App |
| `/clients/` | `clients` | Client Database & Profiles | Clients App |
| `/tasks/` | `tasks` | Task Tracking & Deadlines | Tasks App |
| `/invoices/` | `invoices` | Billing & PDF Generation | Invoices App |
| `/favicon.ico` | — | System favicon redirect | Static |