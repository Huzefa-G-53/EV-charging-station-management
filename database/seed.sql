-- ============================================================
-- EV Charging Station Management System (GreenVolt Energy)
-- Unified Single Seed Data File (Sample / Demo Data)
-- Run AFTER database/schema.sql
-- ============================================================

USE ev_charging_db;

-- 1. Clear existing data in reverse order of foreign key dependencies
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
TRUNCATE TABLE admin;
SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- 1. ADMINISTRATOR
-- Default login: admin@ev.com / admin123
-- ============================================================
INSERT INTO admin (admin_id, full_name, email, password_hash) VALUES
(1, 'System Administrator', 'admin@ev.com', 'scrypt:32768:8:1$t2ub4P0oP2NQcQyr$5b9b65b074bb945a8ac52b6cd10f3b9c85607f52325624d5546bf139e63e009d8dc60f728e9c0b64d1e23d7e0b0953d34bdababbfef9635494474d712f373766');

-- ============================================================
-- 2. CHARGING STATIONS (3 Stations)
-- ============================================================
INSERT INTO charging_station (station_id, station_name, address, contact_number, number_of_chargers, operating_hours, status) VALUES
(1, 'Connaught Place EV Station',    'Block C, Connaught Place, New Delhi - 110001',   '011-23456789', 4, '24 Hours',            'Active'),
(2, 'BKC Green Charging Hub',       'G Block, Bandra Kurla Complex, Mumbai - 400051', '022-98765432', 4, '24 Hours',            'Active'),
(3, 'Indiranagar Charging Station', '100 Feet Road, Indiranagar, Bengaluru - 560038', '080-55443322', 4, '06:00 AM - 11:00 PM', 'Active');

-- ============================================================
-- 3. CHARGERS (4 Chargers per station = 12 total)
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
-- 4. USERS (Customers / Drivers - Default password: user123)
-- ============================================================
INSERT INTO user (user_id, full_name, phone, email, password_hash, address, account_status) VALUES
(1, 'Arjun Sharma', '9876543210', 'arjun@email.com',  'scrypt:32768:8:1$t2ub4P0oP2NQcQyr$5b9b65b074bb945a8ac52b6cd10f3b9c85607f52325624d5546bf139e63e009d8dc60f728e9c0b64d1e23d7e0b0953d34bdababbfef9635494474d712f373766', 'Connaught Place, New Delhi', 'Active'),
(2, 'Rohan Gupta',  '9876543212', 'rohan@email.com',  'scrypt:32768:8:1$t2ub4P0oP2NQcQyr$5b9b65b074bb945a8ac52b6cd10f3b9c85607f52325624d5546bf139e63e009d8dc60f728e9c0b64d1e23d7e0b0953d34bdababbfef9635494474d712f373766', 'Indiranagar, Bengaluru',     'Active'),
(3, 'Sneha Iyer',   '9876543213', 'sneha@email.com',  'scrypt:32768:8:1$t2ub4P0oP2NQcQyr$5b9b65b074bb945a8ac52b6cd10f3b9c85607f52325624d5546bf139e63e009d8dc60f728e9c0b64d1e23d7e0b0953d34bdababbfef9635494474d712f373766', 'South Extension, New Delhi', 'Active'),
(4, 'Vikram Nair',  '9876543214', 'vikram@email.com', 'scrypt:32768:8:1$t2ub4P0oP2NQcQyr$5b9b65b074bb945a8ac52b6cd10f3b9c85607f52325624d5546bf139e63e009d8dc60f728e9c0b64d1e23d7e0b0953d34bdababbfef9635494474d712f373766', 'Juhu, Mumbai',                'Active'),
(5, 'Ananya Das',   '9876543215', 'ananya@email.com', 'scrypt:32768:8:1$t2ub4P0oP2NQcQyr$5b9b65b074bb945a8ac52b6cd10f3b9c85607f52325624d5546bf139e63e009d8dc60f728e9c0b64d1e23d7e0b0953d34bdababbfef9635494474d712f373766', 'Koramangala, Bengaluru',     'Active');

-- ============================================================
-- 5. VEHICLES (Electric Vehicles in Driver Garages)
-- ============================================================
INSERT INTO vehicle (vehicle_id, user_id, vehicle_number, vehicle_type, brand, model, battery_capacity) VALUES
(1, 1, 'DL01AB1234', 'SUV',       'Tata',     'Nexon EV',  40.50),
(2, 2, 'KA03EF7890', 'Sedan',     'Hyundai',  'Ioniq 5',   72.60),
(3, 3, 'DL04GH1122', 'Hatchback', 'Tata',     'Tiago EV',  24.00),
(4, 4, 'MH01IJ3344', 'Sedan',     'BYD',      'Seal',      82.56),
(5, 5, 'KA05KL5566', 'SUV',       'Mahindra', 'XUV400',    39.40);

-- ============================================================
-- 6. STAFF (18 Staff members: 6 per station)
-- Automatically inserts salary expense records into expenses table via trigger
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
(13, 3, 'Iyer Nair',       'Admin',      '9876500003', 'iyer.n@evstation.com',   '2023-01-20', 49000.00),
(14, 3, 'Pooja Desai',     'Manager',    '9876500004', 'pooja@evstation.com',    '2023-04-10', 44000.00),
(15, 3, 'Karthik Reddy',   'Accountant', '9876500005', 'karthik@evstation.com',  '2023-05-15', 35000.00),
(16, 3, 'Anil Gupta',      'Technician', '9876500006', 'anil@evstation.com',     '2023-08-20', 29000.00),
(17, 3, 'Meena Swamy',     'Attendant',  '9876500007', 'meena@evstation.com',    '2023-10-01', 22000.00),
(18, 3, 'Ramesh Gowda',    'Other',      '9876500008', 'ramesh@evstation.com',   '2024-03-01', 20000.00);

-- ============================================================
-- 7. MAINTENANCE (2 Maintenance records)
-- Automatically inserts maintenance expense records into expenses table via trigger
-- ============================================================
INSERT INTO maintenance (maintenance_id, charger_id, staff_id, maintenance_date, issue_description, maintenance_type, cost, status) VALUES
(1, 2, 4,  '2024-11-25', 'Routine connector check and firmware update', 'Preventive', 8000.00,  'Completed'),
(2, 6, 10, '2024-11-28', 'Display screen calibration and cleaning',     'Repair',     12000.00, 'Completed');

-- ============================================================
-- 8. OPERATIONAL EXPENSES (Grid Electricity Bills)
-- ============================================================
INSERT INTO expenses (station_id, expense_date, amount, expense_type, description) VALUES
(1, '2024-12-01', 18000.00, 'Electricity', 'Monthly grid power supply bill - CP Station'),
(2, '2024-12-01', 22000.00, 'Electricity', 'Monthly power supply bill - BKC Hub'),
(3, '2024-12-01', 15000.00, 'Electricity', 'Monthly electricity bill - Indiranagar');

-- ============================================================
-- 9. COMMERCIAL COLLABORATIONS (Partnerships)
-- Automatically inserts revenue records into revenue table via trigger
-- ============================================================
INSERT INTO collaborations (collaboration_id, station_id, partner_name, collaboration_type, contact_person, contact_number, start_date, end_date, agreed_amount, status, description) VALUES
(1, 1, 'PepsiCo India',    'Advertisement Board', 'Rohan Mehta',  '9900001111', '2024-01-01', '2024-12-31',  85000.00, 'Active', 'Billboard on wall facing main road'),
(2, 1, 'Costa Coffee',     'Cafe',                'Seema Pillai', '9900002222', '2024-03-01', '2025-02-28', 160000.00, 'Active', 'Kiosk space inside station premises'),
(3, 2, 'Jio Retail',       'Land Rental',         'Amit Kapoor',  '9900003333', '2024-02-01', '2025-01-31', 220000.00, 'Active', 'Space allocation for customer lounge'),
(4, 2, '7-Eleven Retail',  'Convenience Store',   'Priti Sharma', '9900004444', '2024-04-01', '2025-03-31', 140000.00, 'Active', 'Mini store inside BKC station'),
(5, 3, 'Samsung India',    'Advertisement Board', 'Vikas Roy',    '9900005555', '2024-05-01', '2024-12-31',  95000.00, 'Active', 'Digital display board near entrance'),
(6, 3, 'Starbucks Kiosk',  'Cafe',                'Anil Joshi',   '9900006666', '2024-06-01', '2025-05-31', 135000.00, 'Active', 'Coffee kiosk at Indiranagar station');

-- ============================================================
-- 10. CHARGING SESSIONS & PAYMENTS
-- Completed payments automatically insert revenue records via trigger
-- ============================================================
INSERT INTO charging_session (session_id, user_id, vehicle_id, charger_id, start_time, end_time, energy_consumed, total_amount, status) VALUES
(1,  1, 1, 1,  DATE_SUB(NOW(), INTERVAL 40 MINUTE),  NULL,                                18.50, 333.00, 'Active'),
(2,  2, 2, 6,  DATE_SUB(NOW(), INTERVAL 55 MINUTE),  NULL,                                32.00, 800.00, 'Active'),
(3,  4, 4, 10, DATE_SUB(NOW(), INTERVAL 20 MINUTE),  NULL,                                14.00, 308.00, 'Active'),
(4,  3, 3, 2,  DATE_SUB(NOW(), INTERVAL 195 MINUTE), DATE_SUB(NOW(), INTERVAL 125 MINUTE), 30.00, 660.00, 'Completed'),
(5,  5, 5, 5,  DATE_SUB(NOW(), INTERVAL 300 MINUTE), DATE_SUB(NOW(), INTERVAL 225 MINUTE), 24.50, 490.00, 'Completed'),
(6,  1, 1, 9,  DATE_SUB(NOW(), INTERVAL 390 MINUTE), DATE_SUB(NOW(), INTERVAL 315 MINUTE), 28.00, 504.00, 'Completed'),
(7,  2, 2, 3,  DATE_SUB(NOW(), INTERVAL 28 HOUR),    DATE_SUB(NOW(), INTERVAL 26 HOUR),   35.00, 420.00, 'Completed'),
(8,  4, 4, 7,  DATE_SUB(NOW(), INTERVAL 30 HOUR),    DATE_SUB(NOW(), INTERVAL 28 HOUR),   20.00, 240.00, 'Completed'),
(9,  3, 3, 11, DATE_SUB(NOW(), INTERVAL 32 HOUR),    DATE_SUB(NOW(), INTERVAL 30 HOUR),   15.00, 150.00, 'Completed'),
(10, 5, 5, 4,  DATE_SUB(NOW(), INTERVAL 34 HOUR),    DATE_SUB(NOW(), INTERVAL 33 HOUR),   26.00, 468.00, 'Completed'),
(11, 1, 1, 8,  DATE_SUB(NOW(), INTERVAL 53 HOUR),    DATE_SUB(NOW(), INTERVAL 51 HOUR),   31.00, 620.00, 'Completed'),
(12, 2, 2, 12, DATE_SUB(NOW(), INTERVAL 56 HOUR),    DATE_SUB(NOW(), INTERVAL 55 HOUR),    2.50,  30.00, 'Cancelled');

-- Set chargers to In Use for active sessions
UPDATE charger SET status='In Use' WHERE charger_id IN (1, 6, 10);

-- Insert completed payments for completed sessions
INSERT INTO payment (payment_id, session_id, payment_date, amount, payment_method, payment_status) VALUES
(1, 4,  CURDATE(),                  660.00, 'UPI',         'Completed'),
(2, 5,  CURDATE(),                  490.00, 'Card',        'Completed'),
(3, 6,  CURDATE(),                  504.00, 'Net Banking', 'Completed'),
(4, 7,  DATE_SUB(CURDATE(), INTERVAL 1 DAY), 420.00, 'UPI', 'Completed'),
(5, 8,  DATE_SUB(CURDATE(), INTERVAL 1 DAY), 240.00, 'Cash', 'Completed'),
(6, 9,  DATE_SUB(CURDATE(), INTERVAL 1 DAY), 150.00, 'Wallet', 'Completed'),
(7, 10, DATE_SUB(CURDATE(), INTERVAL 1 DAY), 468.00, 'UPI', 'Completed'),
(8, 11, DATE_SUB(CURDATE(), INTERVAL 2 DAY), 620.00, 'Card', 'Completed');
