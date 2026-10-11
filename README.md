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

### Step 2 — Configure Database Password (`config.py`)

Open `config.py` and set `DB_PASSWORD` to your own local MySQL root password:

```python
class Config:
    DB_HOST     = 'localhost'
    DB_USER     = 'root'
    DB_PASSWORD = 'YOUR_MYSQL_PASSWORD'  # <-- Change this to your password!
    DB_NAME     = 'ev_charging_db'
```

### Step 3 — Create Schema & Load Seed Data

**Option A (Using MySQL Workbench):**
1. Open MySQL Workbench and connect to your local instance.
2. Open and execute `schema.sql` (Click the lightning bolt ⚡ to run all).
3. Open and execute `seed.sql`.

**Option B (Using Windows PowerShell / Terminal):**
```powershell
Get-Content schema.sql | mysql -u root -p
Get-Content seed.sql | mysql -u root -p
```
*(On Mac/Linux: `mysql -u root -p < schema.sql`)*

### Step 4 — Create Admin Account

```bash
python create_admin.py
```

This creates the default administrator login:
- **Email**: `admin@ev.com`
- **Password**: `admin123`

### Step 5 — Start the Application

```bash
python app.py
```

Open your browser and navigate to: **http://127.0.0.1:5000**

---

## Portals & Authentication

The application features **two separate, role-separated portals** accessible from the unified login page:

### 1. 🛡️ Admin & Operational Management Portal
- **Login Credentials**: `admin@ev.com` / `password: admin123`
- **Features**:
  - Live Operational Dashboard & Analytics (Revenue, Expenses, Profit, Charger status)
  - Charging Stations & Chargers management
  - Charging Sessions oversight and Payment ledger
  - Staff management & automated payroll expense tracking
  - Preventive & Repair Maintenance logs
  - Non-charging revenue (Ads, cafe, land lease collaborations)
  - Financial & Operational Reports
  - **Data Privacy Compliance**: Read-only Customer Directory & Vehicle Registry. Administrators cannot tamper with or modify customer personal profiles, credentials, or vehicles.

### 2. ⚡ EV Driver / Customer Self-Service Portal
- **Login Credentials**: e.g., `arjun@email.com` / `password: user123` (or click **"Create a customer account"**)
- **Features**:
  - **Driver Dashboard**: Live active charging monitor, vehicle summary, session counter, total kWh and expenses.
  - **My EV Garage**: Add, edit, and delete personally owned electric vehicles (license plate, make, model, battery capacity).
  - **Station Finder**: Browse network stations with real-time bay availability, power ratings, and tariffs.
  - **Initiate & Stop Charging**: Select vehicle, connect to an available charger bay, monitor live session, and unplug with automated meter billing.
  - **Invoices & Payments**: View billing breakdown, settle payments (UPI, Card, Net Banking, Wallet), and print official receipts.
  - **Profile & Security**: Update personal contact info, change password, and permanent self-deletion ("Right to be Forgotten").

---

## Modules Available

| Module | URL Prefix | Target Role | Key Features |
|---|---|---|---|
| Admin Dashboard | /dashboard | Admin | KPIs, 4 interactive charts |
| Customer Directory | /users/ | Admin | Read-only profile overview + status toggle |
| Vehicle Registry | /vehicles/ | Admin | On-site plate lookup & walk-in entry |
| Stations & Chargers | /stations/, /chargers/ | Admin | Network infrastructure & pricing |
| Sessions & Payments | /sessions/, /payments/ | Admin | Operations ledger & audit logs |
| Staff & Maintenance | /staff/, /maintenance/ | Admin | Personnel & charger maintenance |
| Financials | /expenses/, /revenue/, /collaborations/ | Admin | Comprehensive balance sheet |
| Reports | /reports/ | Admin | Station-wise performance & analytics |
| Driver Dashboard | /customer/dashboard | Customer | Driver overview & live charge tracker |
| My Garage | /customer/vehicles | Customer | Personal vehicle fleet management |
| Station Finder | /customer/stations | Customer | Real-time bay availability & tariffs |
| Charging Operations | /customer/sessions | Customer | Initiate/Stop charging sessions |
| Billing & Receipts | /customer/payments | Customer | Pay pending bills & print receipts |
| Profile & Privacy | /customer/profile | Customer | Self-service edit, password change, account deletion |

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
