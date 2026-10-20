"""
Single Unified Seed Script for EV Charging Management System (GreenVolt Energy)
Seeds all tables in the correct relational order with proper password hashing,
live active sessions, realistic historical sessions, and financial data.
Usage:
    python database/seed.py
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import mysql.connector
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from config import Config


def run_seed():
    print("[*] Connecting to MySQL database:", Config.DB_NAME)
    cnx = mysql.connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME
    )
    cursor = cnx.cursor(dictionary=True)

    print("[*] Cleaning existing data in reverse dependency order...")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    tables = [
        'collaborations', 'revenue', 'expenses', 'maintenance',
        'payment', 'charging_session', 'staff', 'charger',
        'charging_station', 'vehicle', 'user', 'admin'
    ]
    for table in tables:
        cursor.execute(f"TRUNCATE TABLE {table};")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

    # ── 1. Admin Account ───────────────────────────────────────────────────────
    print("[+] Seeding Administrator account...")
    admin_hash = generate_password_hash('admin123')
    cursor.execute(
        '''INSERT INTO admin (admin_id, full_name, email, password_hash)
           VALUES (1, 'System Administrator', 'admin@ev.com', %s)''',
        (admin_hash,)
    )

    # ── 2. Charging Stations ───────────────────────────────────────────────────
    print("[+] Seeding Charging Stations...")
    cursor.execute(
        '''INSERT INTO charging_station (station_id, station_name, address, contact_number, number_of_chargers, operating_hours, status) VALUES
           (1, 'Connaught Place EV Station',    'Block C, Connaught Place, New Delhi - 110001',   '011-23456789', 4, '24 Hours',            'Active'),
           (2, 'BKC Green Charging Hub',       'G Block, Bandra Kurla Complex, Mumbai - 400051', '022-98765432', 4, '24 Hours',            'Active'),
           (3, 'Indiranagar Charging Station', '100 Feet Road, Indiranagar, Bengaluru - 560038', '080-55443322', 4, '06:00 AM - 11:00 PM', 'Active')'''
    )

    # ── 3. Chargers ────────────────────────────────────────────────────────────
    print("[+] Seeding Chargers...")
    cursor.execute(
        '''INSERT INTO charger (charger_id, station_id, charger_type, power_rating, price_per_kwh, status) VALUES
           -- Station 1 (Delhi)
           (1,  1, 'DC Fast (CCS2)',      50.00, 18.00, 'Available'),
           (2,  1, 'DC Fast (CCS2)',     120.00, 22.00, 'Available'),
           (3,  1, 'AC Level 2 (Type 2)', 22.00, 12.00, 'Available'),
           (4,  1, 'DC Fast (CHAdeMO)',   50.00, 18.00, 'Available'),
           -- Station 2 (Mumbai)
           (5,  2, 'DC Fast (CCS2)',      60.00, 20.00, 'Available'),
           (6,  2, 'DC Fast (CCS2)',     150.00, 25.00, 'Available'),
           (7,  2, 'AC Level 2 (Type 2)', 22.00, 12.00, 'Available'),
           (8,  2, 'DC Fast (CCS2)',      60.00, 20.00, 'Available'),
           -- Station 3 (Bengaluru)
           (9,  3, 'DC Fast (CCS2)',      50.00, 18.00, 'Available'),
           (10, 3, 'DC Fast (CCS2)',     100.00, 22.00, 'Available'),
           (11, 3, 'AC Level 2 (Type 2)', 11.00, 10.00, 'Available'),
           (12, 3, 'AC Level 2 (Type 2)', 22.00, 12.00, 'Available')'''
    )

    # ── 4. Customers (Drivers) ─────────────────────────────────────────────────
    print("[+] Seeding Registered Drivers...")
    user_hash = generate_password_hash('user123')
    drivers = [
        (1, 'Arjun Sharma', '9876543210', 'arjun@email.com',  user_hash, 'Connaught Place, New Delhi', 'Active'),
        (2, 'Rohan Gupta',  '9876543212', 'rohan@email.com',  user_hash, 'Indiranagar, Bengaluru',     'Active'),
        (3, 'Sneha Iyer',   '9876543213', 'sneha@email.com',  user_hash, 'South Extension, New Delhi', 'Active'),
        (4, 'Vikram Nair',  '9876543214', 'vikram@email.com', user_hash, 'Juhu, Mumbai',                'Active'),
        (5, 'Ananya Das',   '9876543215', 'ananya@email.com', user_hash, 'Koramangala, Bengaluru',     'Active')
    ]
    cursor.executemany(
        '''INSERT INTO user (user_id, full_name, phone, email, password_hash, address, account_status)
           VALUES (%s, %s, %s, %s, %s, %s, %s)''',
        drivers
    )

    # ── 5. Vehicles (Garage) ───────────────────────────────────────────────────
    print("[+] Seeding Electric Vehicles...")
    vehicles = [
        (1, 1, 'DL01AB1234', 'SUV',       'Tata',     'Nexon EV',  40.50),
        (2, 2, 'KA03EF7890', 'Sedan',     'Hyundai',  'Ioniq 5',   72.60),
        (3, 3, 'DL04GH1122', 'Hatchback', 'Tata',     'Tiago EV',  24.00),
        (4, 4, 'MH01IJ3344', 'Sedan',     'BYD',      'Seal',      82.56),
        (5, 5, 'KA05KL5566', 'SUV',       'Mahindra', 'XUV400',    39.40)
    ]
    cursor.executemany(
        '''INSERT INTO vehicle (vehicle_id, user_id, vehicle_number, vehicle_type, brand, model, battery_capacity)
           VALUES (%s, %s, %s, %s, %s, %s, %s)''',
        vehicles
    )

    # ── 6. Staff (Triggers Auto-Salary Expenses) ───────────────────────────────
    print("[+] Seeding Station Staff...")
    cursor.execute(
        '''INSERT INTO staff (staff_id, station_id, full_name, role, phone, email, joining_date, salary) VALUES
           -- Station 1 (New Delhi)
           (1,  1, 'Rajesh Sharma',   'Admin',      '9876511111', 'rajesh@evstation.com',   '2023-01-15', 50000.00),
           (2,  1, 'Mohammed Iqbal',  'Manager',    '9876522222', 'iqbal@evstation.com',    '2023-03-10', 45000.00),
           (3,  1, 'Neha Kapoor',     'Accountant', '9876533311', 'neha@evstation.com',     '2023-04-01', 36000.00),
           (4,  1, 'Suresh Patil',    'Technician', '9876533333', 'suresh@evstation.com',   '2023-05-20', 30000.00),
           (5,  1, 'Kavita Shah',     'Attendant',  '9876544444', 'kavita@evstation.com',   '2023-08-01', 24000.00),
           (6,  1, 'Rahul Verma',     'Other',      '9876566666', 'rahul@evstation.com',    '2024-01-10', 21000.00),
           -- Station 2 (Mumbai)
           (7,  2, 'Vikram Malhotra', 'Admin',      '9876577777', 'vikram.m@evstation.com', '2023-02-01', 48000.00),
           (8,  2, 'Deepak Joshi',    'Manager',    '9876588888', 'deepak@evstation.com',   '2023-03-15', 43000.00),
           (9,  2, 'Ananya Roy',      'Accountant', '9876555555', 'ananya@evstation.com',   '2023-06-01', 37000.00),
           (10, 2, 'Anjali Rao',      'Technician', '9876599999', 'anjali@evstation.com',   '2023-07-10', 32000.00),
           (11, 2, 'Ravi Kumar',      'Attendant',  '9876500001', 'ravi@evstation.com',     '2023-09-01', 23000.00),
           (12, 2, 'Sunil Shinde',    'Other',      '9876500002', 'sunil@evstation.com',    '2024-02-01', 20000.00),
           -- Station 3 (Bengaluru)
           (13, 3, 'Iyer Nair',       'Admin',      '9876500003', 'iyer.n@evstation.com',   '2023-01-20', 49000.00),
           (14, 3, 'Pooja Desai',     'Manager',    '9876500004', 'pooja@evstation.com',    '2023-04-10', 44000.00),
           (15, 3, 'Karthik Reddy',   'Accountant', '9876500005', 'karthik@evstation.com',  '2023-05-15', 35000.00),
           (16, 3, 'Anil Gupta',      'Technician', '9876500006', 'anil@evstation.com',     '2023-08-20', 29000.00),
           (17, 3, 'Meena Swamy',     'Attendant',  '9876500007', 'meena@evstation.com',    '2023-10-01', 22000.00),
           (18, 3, 'Ramesh Gowda',    'Other',      '9876500008', 'ramesh@evstation.com',   '2024-03-01', 20000.00)'''
    )

    # ── 7. Maintenance Records (Triggers Auto-Maintenance Expenses) ───────────
    print("[+] Seeding Maintenance Records...")
    cursor.execute(
        '''INSERT INTO maintenance (maintenance_id, charger_id, staff_id, maintenance_date, issue_description, maintenance_type, cost, status) VALUES
           (1, 2, 4,  '2024-11-25', 'Routine connector check and firmware update', 'Preventive', 8000.00,  'Completed'),
           (2, 6, 10, '2024-11-28', 'Display screen calibration and cleaning',     'Repair',     12000.00, 'Completed')'''
    )

    # ── 8. Operational Expenses (Electricity) ──────────────────────────────────
    print("[+] Seeding Power & Electricity Expenses...")
    cursor.execute(
        '''INSERT INTO expenses (station_id, expense_date, amount, expense_type, description) VALUES
           (1, '2024-12-01', 18000.00, 'Electricity', 'Monthly grid power supply bill - CP Station'),
           (2, '2024-12-01', 22000.00, 'Electricity', 'Monthly power supply bill - BKC Hub'),
           (3, '2024-12-01', 15000.00, 'Electricity', 'Monthly electricity bill - Indiranagar')'''
    )

    # ── 9. Commercial Collaborations (Triggers Auto-Revenue) ───────────────────
    print("[+] Seeding Commercial Collaborations...")
    cursor.execute(
        '''INSERT INTO collaborations (collaboration_id, station_id, partner_name, collaboration_type, contact_person, contact_number, start_date, end_date, agreed_amount, status, description) VALUES
           (1, 1, 'PepsiCo India',    'Advertisement Board', 'Rohan Mehta',  '9900001111', '2024-01-01', '2024-12-31',  85000.00, 'Active', 'Billboard on wall facing main road'),
           (2, 1, 'Costa Coffee',     'Cafe',                'Seema Pillai', '9900002222', '2024-03-01', '2025-02-28', 160000.00, 'Active', 'Kiosk space inside station premises'),
           (3, 2, 'Jio Retail',       'Land Rental',         'Amit Kapoor',  '9900003333', '2024-02-01', '2025-01-31', 220000.00, 'Active', 'Space allocation for customer lounge'),
           (4, 2, '7-Eleven Retail',  'Convenience Store',   'Priti Sharma', '9900004444', '2024-04-01', '2025-03-31', 140000.00, 'Active', 'Mini store inside BKC station'),
           (5, 3, 'Samsung India',    'Advertisement Board', 'Vikas Roy',    '9900005555', '2024-05-01', '2024-12-31',  95000.00, 'Active', 'Digital display board near entrance'),
           (6, 3, 'Starbucks Kiosk',  'Cafe',                'Anil Joshi',   '9900006666', '2024-06-01', '2025-05-31', 135000.00, 'Active', 'Coffee kiosk at Indiranagar station')'''
    )

    # ── 10. Charging Sessions & Payments (Dynamic Timeline & Active Live Bays) ─
    print("[+] Seeding Timeline Sessions and Real-Time Charging...")
    now = datetime.now()

    sessions = [
        # Active charging right now (Live status: In Use)
        {
            'user_id': 1, 'vehicle_id': 1, 'charger_id': 1,
            'start_time': now - timedelta(minutes=40), 'end_time': None,
            'energy_consumed': 18.50, 'total_amount': 333.00, 'status': 'Active'
        },
        {
            'user_id': 2, 'vehicle_id': 2, 'charger_id': 6,
            'start_time': now - timedelta(minutes=55), 'end_time': None,
            'energy_consumed': 32.00, 'total_amount': 800.00, 'status': 'Active'
        },
        {
            'user_id': 4, 'vehicle_id': 4, 'charger_id': 10,
            'start_time': now - timedelta(minutes=20), 'end_time': None,
            'energy_consumed': 14.00, 'total_amount': 308.00, 'status': 'Active'
        },
        # Completed sessions today
        {
            'user_id': 3, 'vehicle_id': 3, 'charger_id': 2,
            'start_time': now - timedelta(hours=3, minutes=15), 'end_time': now - timedelta(hours=2, minutes=5),
            'energy_consumed': 30.00, 'total_amount': 660.00, 'status': 'Completed',
            'payment': {'method': 'UPI', 'date': now.date()}
        },
        {
            'user_id': 5, 'vehicle_id': 5, 'charger_id': 5,
            'start_time': now - timedelta(hours=5), 'end_time': now - timedelta(hours=3, minutes=45),
            'energy_consumed': 24.50, 'total_amount': 490.00, 'status': 'Completed',
            'payment': {'method': 'Card', 'date': now.date()}
        },
        {
            'user_id': 1, 'vehicle_id': 1, 'charger_id': 9,
            'start_time': now - timedelta(hours=6, minutes=30), 'end_time': now - timedelta(hours=5, minutes=15),
            'energy_consumed': 28.00, 'total_amount': 504.00, 'status': 'Completed',
            'payment': {'method': 'Net Banking', 'date': now.date()}
        },
        # Completed sessions yesterday
        {
            'user_id': 2, 'vehicle_id': 2, 'charger_id': 3,
            'start_time': now - timedelta(days=1, hours=4), 'end_time': now - timedelta(days=1, hours=2, minutes=45),
            'energy_consumed': 35.00, 'total_amount': 420.00, 'status': 'Completed',
            'payment': {'method': 'UPI', 'date': (now - timedelta(days=1)).date()}
        },
        {
            'user_id': 4, 'vehicle_id': 4, 'charger_id': 7,
            'start_time': now - timedelta(days=1, hours=6), 'end_time': now - timedelta(days=1, hours=4, minutes=30),
            'energy_consumed': 20.00, 'total_amount': 240.00, 'status': 'Completed',
            'payment': {'method': 'Cash', 'date': (now - timedelta(days=1)).date()}
        },
        {
            'user_id': 3, 'vehicle_id': 3, 'charger_id': 11,
            'start_time': now - timedelta(days=1, hours=8), 'end_time': now - timedelta(days=1, hours=6, minutes=45),
            'energy_consumed': 15.00, 'total_amount': 150.00, 'status': 'Completed',
            'payment': {'method': 'Wallet', 'date': (now - timedelta(days=1)).date()}
        },
        {
            'user_id': 5, 'vehicle_id': 5, 'charger_id': 4,
            'start_time': now - timedelta(days=1, hours=10), 'end_time': now - timedelta(days=1, hours=9),
            'energy_consumed': 26.00, 'total_amount': 468.00, 'status': 'Completed',
            'payment': {'method': 'UPI', 'date': (now - timedelta(days=1)).date()}
        },
        # 2 days ago
        {
            'user_id': 1, 'vehicle_id': 1, 'charger_id': 8,
            'start_time': now - timedelta(days=2, hours=5), 'end_time': now - timedelta(days=2, hours=3, minutes=45),
            'energy_consumed': 31.00, 'total_amount': 620.00, 'status': 'Completed',
            'payment': {'method': 'Card', 'date': (now - timedelta(days=2)).date()}
        },
        {
            'user_id': 2, 'vehicle_id': 2, 'charger_id': 12,
            'start_time': now - timedelta(days=2, hours=8), 'end_time': now - timedelta(days=2, hours=7, minutes=45),
            'energy_consumed': 2.50, 'total_amount': 30.00, 'status': 'Cancelled'
        },
        # 3 days ago
        {
            'user_id': 3, 'vehicle_id': 3, 'charger_id': 1,
            'start_time': now - timedelta(days=3, hours=4), 'end_time': now - timedelta(days=3, hours=2, minutes=50),
            'energy_consumed': 25.00, 'total_amount': 450.00, 'status': 'Completed',
            'payment': {'method': 'UPI', 'date': (now - timedelta(days=3)).date()}
        },
        {
            'user_id': 5, 'vehicle_id': 5, 'charger_id': 6,
            'start_time': now - timedelta(days=3, hours=7), 'end_time': now - timedelta(days=3, hours=5, minutes=30),
            'energy_consumed': 29.00, 'total_amount': 725.00, 'status': 'Completed',
            'payment': {'method': 'Card', 'date': (now - timedelta(days=3)).date()}
        },
        # 4 days ago
        {
            'user_id': 4, 'vehicle_id': 4, 'charger_id': 10,
            'start_time': now - timedelta(days=4, hours=5), 'end_time': now - timedelta(days=4, hours=3, minutes=45),
            'energy_consumed': 22.00, 'total_amount': 484.00, 'status': 'Completed',
            'payment': {'method': 'Wallet', 'date': (now - timedelta(days=4)).date()}
        },
        {
            'user_id': 1, 'vehicle_id': 1, 'charger_id': 3,
            'start_time': now - timedelta(days=4, hours=8), 'end_time': now - timedelta(days=4, hours=7),
            'energy_consumed': 18.00, 'total_amount': 216.00, 'status': 'Completed',
            'payment': {'method': 'Cash', 'date': (now - timedelta(days=4)).date()}
        },
        # 5 days ago
        {
            'user_id': 2, 'vehicle_id': 2, 'charger_id': 5,
            'start_time': now - timedelta(days=5, hours=6), 'end_time': now - timedelta(days=5, hours=4, minutes=40),
            'energy_consumed': 27.50, 'total_amount': 550.00, 'status': 'Completed',
            'payment': {'method': 'UPI', 'date': (now - timedelta(days=5)).date()}
        },
        # 6 days ago
        {
            'user_id': 3, 'vehicle_id': 3, 'charger_id': 9,
            'start_time': now - timedelta(days=6, hours=5), 'end_time': now - timedelta(days=6, hours=3, minutes=30),
            'energy_consumed': 32.00, 'total_amount': 576.00, 'status': 'Completed',
            'payment': {'method': 'Net Banking', 'date': (now - timedelta(days=6)).date()}
        }
    ]

    for s in sessions:
        cursor.execute(
            '''INSERT INTO charging_session (user_id, vehicle_id, charger_id, start_time, end_time, energy_consumed, total_amount, status)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
            (s['user_id'], s['vehicle_id'], s['charger_id'], s['start_time'], s['end_time'], s['energy_consumed'], s['total_amount'], s['status'])
        )
        session_id = cursor.lastrowid

        if s['status'] == 'Active':
            cursor.execute("UPDATE charger SET status='In Use' WHERE charger_id=%s", (s['charger_id'],))

        if 'payment' in s and s['payment']:
            p = s['payment']
            cursor.execute(
                '''INSERT INTO payment (session_id, payment_date, amount, payment_method, payment_status)
                   VALUES (%s, %s, %s, %s, 'Completed')''',
                (session_id, p['date'], s['total_amount'], p['method'])
            )

    cnx.commit()
    cursor.close()
    cnx.close()
    print("[OK] Complete database seeded successfully with all tables and live timeline data!")


if __name__ == '__main__':
    run_seed()
