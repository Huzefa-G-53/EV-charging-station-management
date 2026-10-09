-- ============================================================
-- EV Charging Station Management System
-- Seed Data (Sample / Demo Data)
-- Run AFTER schema.sql and AFTER running create_admin.py
-- ============================================================

USE ev_charging_db;

-- Clear existing data in reverse order of dependencies
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE collaborations;
TRUNCATE TABLE revenue;
TRUNCATE TABLE expenses;
TRUNCATE TABLE maintenance;
TRUNCATE TABLE payment;
TRUNCATE TABLE charging_session;
TRUNCATE TABLE staff;
TRUNCATE TABLE charger;
TRUNCATE TABLE charging_station;
TRUNCATE TABLE vehicle;
TRUNCATE TABLE user;
SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- 1. CHARGING STATIONS (3 Stations in different locations)
-- ============================================================
INSERT INTO charging_station (station_id, station_name, address, contact_number, number_of_chargers, operating_hours, status) VALUES
(1, 'Connaught Place EV Station',     'Block C, Connaught Place, New Delhi - 110001',           '011-23456789', 4, '24 Hours',            'Active'),
(2, 'BKC Green Charging Hub',        'G Block, Bandra Kurla Complex, Mumbai - 400051',         '022-98765432', 4, '24 Hours',            'Active'),
(3, 'Indiranagar Charging Station',  '100 Feet Road, Indiranagar, Bengaluru - 560038',         '080-55443322', 4, '06:00 AM - 11:00 PM', 'Active');

-- ============================================================
-- 2. CHARGERS (4 Chargers per station = 12 total)
-- ============================================================
INSERT INTO charger (charger_id, station_id, charger_type, power_rating, price_per_kwh, status) VALUES
-- Station 1 (New Delhi)
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
(12, 3, 'AC Level 2 (Type 2)', 22.00, 12.00, 'Available');

-- ============================================================
-- 3. USERS (6 Users)
-- ============================================================
INSERT INTO user (user_id, full_name, phone, email, password_hash, address, account_status) VALUES
(1, 'Arjun Sharma', '9876543210', 'arjun@email.com', 'placeholder_hash', 'Connaught Place, New Delhi', 'Active'),
(2, 'sanjay Mehta',  '9876543211', 'sanjay@email.com', 'placeholder_hash', 'Bandra West, Mumbai',        'Active'),
(3, 'Rohan Gupta',  '9876543212', 'rohan@email.com', 'placeholder_hash', 'Indiranagar, Bengaluru',     'Active'),
(4, 'Sneha Iyer',   '9876543213', 'sneha@email.com', 'placeholder_hash', 'South Extension, New Delhi', 'Active'),
(5, 'Vikram Nair',  '9876543214', 'vikram@email.com', 'placeholder_hash', 'Juhu, Mumbai',                'Active'),
(6, 'Ananya Das',   '9876543215', 'ananya@email.com', 'placeholder_hash', 'Koramangala, Bengaluru',     'Active');

-- ============================================================
-- 4. VEHICLES (6 Vehicles owned by users)
-- ============================================================
INSERT INTO vehicle (vehicle_id, user_id, vehicle_number, vehicle_type, brand, model, battery_capacity) VALUES
(1, 1, 'DL01AB1234', 'SUV',       'Tata',    'Nexon EV',  40.50),
(2, 2, 'MH02CD3456', 'SUV',       'MG',      'ZS EV',     50.30),
(3, 3, 'KA03EF7890', 'Sedan',     'Hyundai', 'Ioniq 5',   72.60),
(4, 4, 'DL04GH1122', 'Hatchback', 'Tata',    'Tiago EV',  24.00),
(5, 5, 'MH01IJ3344', 'Sedan',     'BYD',     'Seal',      82.56),
(6, 6, 'KA05KL5566', 'SUV',       'Mahindra','XUV400',    39.40);

-- ============================================================
-- 5. STAFF (18 Staff members: 6 per station with position-based salary range ₹20k - ₹50k)
-- Adding staff will automatically trigger salary insertion into expenses!
-- ============================================================
INSERT INTO staff (staff_id, station_id, full_name, role, phone, email, joining_date, salary) VALUES
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
(13, 3, 'Iyer Nair',      'Admin',      '9876500003', 'iyer.n@evstation.com',  '2023-01-20', 49000.00),
(14, 3, 'Pooja Desai',     'Manager',    '9876500004', 'pooja@evstation.com',    '2023-04-10', 44000.00),
(15, 3, 'Karthik Reddy',   'Accountant', '9876500005', 'karthik@evstation.com',  '2023-05-15', 35000.00),
(16, 3, 'Anil Gupta',      'Technician', '9876500006', 'anil@evstation.com',     '2023-08-20', 29000.00),
(17, 3, 'Meena Swamy',     'Attendant',  '9876500007', 'meena@evstation.com',    '2023-10-01', 22000.00),
(18, 3, 'Ramesh Gowda',    'Other',      '9876500008', 'ramesh@evstation.com',   '2024-03-01', 20000.00);

-- ============================================================
-- 6. CHARGING SESSIONS (12 Sessions: Every charger has 1 completed session)
-- ============================================================
INSERT INTO charging_session (session_id, user_id, vehicle_id, charger_id, start_time, end_time, energy_consumed, total_amount, status) VALUES
(1,  1, 1, 1,  '2024-12-01 08:00:00', '2024-12-01 09:00:00', 30.00, 3600.00, 'Completed'),
(2,  2, 2, 2,  '2024-12-01 09:30:00', '2024-12-01 10:45:00', 40.00, 4800.00, 'Completed'),
(3,  3, 3, 3,  '2024-12-01 11:00:00', '2024-12-01 12:30:00', 25.00, 3000.00, 'Completed'),
(4,  4, 4, 4,  '2024-12-01 14:00:00', '2024-12-01 15:00:00', 20.00, 2400.00, 'Completed'),
(5,  5, 5, 5,  '2024-12-02 08:30:00', '2024-12-02 09:30:00', 35.00, 4200.00, 'Completed'),
(6,  6, 6, 6,  '2024-12-02 10:00:00', '2024-12-02 11:00:00', 45.00, 5400.00, 'Completed'),
(7,  1, 1, 7,  '2024-12-02 13:00:00', '2024-12-02 14:30:00', 20.00, 2400.00, 'Completed'),
(8,  2, 2, 8,  '2024-12-02 15:00:00', '2024-12-02 16:00:00', 30.00, 3600.00, 'Completed'),
(9,  3, 3, 9,  '2024-12-03 09:00:00', '2024-12-03 10:00:00', 35.00, 4200.00, 'Completed'),
(10, 4, 4, 10, '2024-12-03 11:00:00', '2024-12-03 12:15:00', 40.00, 4800.00, 'Completed'),
(11, 5, 5, 11, '2024-12-03 13:30:00', '2024-12-03 15:00:00', 18.00, 2160.00, 'Completed'),
(12, 6, 6, 12, '2024-12-03 16:00:00', '2024-12-03 17:30:00', 24.00, 2880.00, 'Completed');

-- ============================================================
-- 7. PAYMENTS (12 Payments for the 12 completed sessions)
-- Adding completed payments automatically triggers revenue entries into revenue table!
-- ============================================================
INSERT INTO payment (payment_id, session_id, payment_date, amount, payment_method, payment_status) VALUES
(1,  1,  '2024-12-01', 3600.00, 'UPI',         'Completed'),
(2,  2,  '2024-12-01', 4800.00, 'Card',        'Completed'),
(3,  3,  '2024-12-01', 3000.00, 'Cash',        'Completed'),
(4,  4,  '2024-12-01', 2400.00, 'UPI',         'Completed'),
(5,  5,  '2024-12-02', 4200.00, 'Net Banking', 'Completed'),
(6,  6,  '2024-12-02', 5400.00, 'Card',        'Completed'),
(7,  7,  '2024-12-02', 2400.00, 'Wallet',      'Completed'),
(8,  8,  '2024-12-02', 3600.00, 'UPI',         'Completed'),
(9,  9,  '2024-12-03', 4200.00, 'UPI',         'Completed'),
(10, 10, '2024-12-03', 4800.00, 'Card',        'Completed'),
(11, 11, '2024-12-03', 2160.00, 'Cash',        'Completed'),
(12, 12, '2024-12-03', 2880.00, 'UPI',         'Completed');

-- ============================================================
-- 8. MAINTENANCE (2 Maintenance records)
-- Adding maintenance with cost automatically triggers maintenance expense into expenses table!
-- ============================================================
INSERT INTO maintenance (maintenance_id, charger_id, staff_id, maintenance_date, issue_description, maintenance_type, cost, status) VALUES
(1, 2, 4, '2024-11-25', 'Routine connector check and firmware update', 'Preventive', 8000.00,  'Completed'),
(2, 6, 10,'2024-11-28', 'Display screen calibration and cleaning',     'Repair',     12000.00, 'Completed');

-- ============================================================
-- 9. ADDITIONAL MANUAL EXPENSES (Electricity, Utilities)
-- Salary and Maintenance expenses are automatically added by triggers above!
-- ============================================================
INSERT INTO expenses (station_id, expense_date, amount, expense_type, description) VALUES
(1, '2024-12-01', 18000.00, 'Electricity', 'Monthly grid power supply bill - CP Station'),
(2, '2024-12-01', 22000.00, 'Electricity', 'Monthly power supply bill - BKC Hub'),
(3, '2024-12-01', 15000.00, 'Electricity', 'Monthly electricity bill - Indiranagar');

-- ============================================================
-- 10. COLLABORATIONS (Business partnership agreements)
-- Active collaborations automatically trigger revenue entries into revenue table!
-- ============================================================
INSERT INTO collaborations (collaboration_id, station_id, partner_name, collaboration_type, contact_person, contact_number, start_date, end_date, agreed_amount, status, description) VALUES
(1, 1, 'PepsiCo India',    'Advertisement Board', 'Rohan Mehta',  '9900001111', '2024-01-01', '2024-12-31', 85000.00,  'Active', 'Billboard on wall facing main road'),
(2, 1, 'Costa Coffee',     'Cafe',                'Seema Pillai', '9900002222', '2024-03-01', '2025-02-28', 160000.00, 'Active', 'Kiosk space inside station premises'),
(3, 2, 'Jio Retail',       'Land Rental',         'Amit Kapoor',  '9900003333', '2024-02-01', '2025-01-31', 220000.00, 'Active', 'Space allocation for customer lounge'),
(4, 2, '7-Eleven Retail',  'Convenience Store',   'Priti Sharma', '9900004444', '2024-04-01', '2025-03-31', 140000.00, 'Active', 'Mini store inside BKC station'),
(5, 3, 'Samsung India',    'Advertisement Board', 'Vikas Roy',    '9900005555', '2024-05-01', '2024-12-31', 95000.00,  'Active', 'Digital display board near entrance'),
(6, 3, 'Starbucks Kiosk',  'Cafe',                'Anil Joshi',   '9900006666', '2024-06-01', '2025-05-31', 135000.00, 'Active', 'Coffee kiosk at Indiranagar station');
