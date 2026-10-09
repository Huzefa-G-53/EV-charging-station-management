# EV Charging Station Management System

A full-stack Flask + MySQL admin panel for managing EV charging station operations.

---

## Tech Stack

- **Backend**: Python 3.10+, Flask 3.x, mysql-connector-python
- **Database**: MySQL 8.x
- **Frontend**: Bootstrap 5 (CDN) + Custom CSS + Chart.js (CDN)

---

## Project Structure

```
ev-charging-management/
├── app.py                    # Flask entry point
├── config.py                 # DB credentials & secret key
├── create_admin.py           # One-time admin account setup script
├── requirements.txt
├── schema.sql                # Database schema (run first)
├── seed.sql                  # Sample data (run after schema)
├── sql_queries.sql           # All important SQL queries (for report)
├── database/
│   └── db_connection.py      # MySQL connection & execute_query helper
├── routes/                   # One Blueprint per module
│   ├── auth_routes.py
│   ├── dashboard_routes.py
│   ├── user_routes.py
│   ├── vehicle_routes.py
│   ├── station_routes.py
│   ├── charger_routes.py
│   ├── session_routes.py
│   ├── payment_routes.py
│   ├── staff_routes.py
│   ├── maintenance_routes.py
│   ├── expense_routes.py
│   ├── revenue_routes.py
│   ├── collaboration_routes.py
│   └── report_routes.py
├── templates/                # Jinja2 HTML templates
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── *_list.html           # List page per module
│   ├── *_form.html           # Add/Edit form per module
│   └── reports.html
└── static/
    ├── css/style.css
    └── js/script.js
```

---

## Setup Instructions

### Step 1 — Install Python dependencies

```bash
cd ev-charging-management
pip install -r requirements.txt
```

### Step 2 — Create the MySQL Database & Schema

Open **MySQL Workbench** or run from terminal:

```bash
mysql -u root -p < schema.sql
```

### Step 3 — Load Sample Data

```bash
mysql -u root -p < seed.sql
```

### Step 4 — Create the Admin Account

```bash
python create_admin.py
```

This creates the admin login:
- **Email**: `admin@ev.com`
- **Password**: `admin123`

### Step 5 — Run the Application

```bash
python app.py
```

Open your browser and go to: **http://127.0.0.1:5000**

---

## Admin Login

| Field    | Value           |
|----------|-----------------|
| Email    | admin@ev.com    |
| Password | admin123        |

---

## Modules Available

| Module         | URL Prefix        | Features                        |
|----------------|-------------------|---------------------------------|
| Dashboard      | /dashboard        | KPIs, 4 charts                  |
| Users          | /users/           | CRUD + search                   |
| Vehicles       | /vehicles/        | CRUD + search                   |
| Stations       | /stations/        | CRUD + search                   |
| Chargers       | /chargers/        | CRUD + station filter           |
| Sessions       | /sessions/        | CRUD + status filter            |
| Payments       | /payments/        | CRUD + status filter            |
| Staff          | /staff/           | CRUD + station filter           |
| Maintenance    | /maintenance/     | CRUD + status filter            |
| Expenses       | /expenses/        | CRUD + type & station filter    |
| Revenue        | /revenue/         | CRUD + source & station filter  |
| Collaborations | /collaborations/  | CRUD + status & station filter  |
| Reports        | /reports/         | Financial + operational reports |

---

## Database Tables

| Table              | Description                            |
|--------------------|----------------------------------------|
| admin              | Admin login credentials                |
| user               | Registered EV users                    |
| vehicle            | User-owned vehicles                    |
| charging_station   | Physical station locations             |
| charger            | Individual charger units               |
| charging_session   | EV charging session records            |
| payment            | Payments for sessions (1:1)            |
| staff              | Station staff members                  |
| maintenance        | Charger maintenance records            |
| expenses           | Station expense records                |
| revenue            | Station income records                 |
| collaborations     | Business partnership agreements        |

---

## Important Relationships

```
USER          1:M  VEHICLE
USER          1:M  CHARGING_SESSION
VEHICLE       1:M  CHARGING_SESSION
CHARGING_STATION 1:M  CHARGER
CHARGER       1:M  CHARGING_SESSION
CHARGING_SESSION 1:1  PAYMENT
CHARGING_STATION 1:M  STAFF
CHARGER       1:M  MAINTENANCE
STAFF         1:M  MAINTENANCE
CHARGING_STATION 1:M  EXPENSES
CHARGING_STATION 1:M  REVENUE
CHARGING_STATION 1:M  COLLABORATIONS
```

---

## Configuration

Edit `config.py` to change database credentials:

```python
class Config:
    DB_HOST     = 'localhost'
    DB_USER     = 'root'
    DB_PASSWORD = 'your_password'
    DB_NAME     = 'ev_charging_db'
    SECRET_KEY  = 'your_secret_key'
    DEBUG       = True
```

---

## SQL Queries

All important SQL queries used in the project are documented in `sql_queries.sql` with comments. Use this file for the DBMS project report and viva preparation.
