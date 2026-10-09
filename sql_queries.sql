-- ============================================================
-- EV Charging Station Management System
-- Important SQL Queries for DBMS Project Report & Viva
-- ============================================================

USE ev_charging_db;

-- ============================================================
-- SECTION 1: INSERT QUERIES (Adding Records)
-- ============================================================

-- 1.1 Add a new user
INSERT INTO user (full_name, phone, email, password_hash, address, account_status)
VALUES ('John Doe', '9876500000', 'john@email.com', 'hashed_password', 'Mumbai', 'Active');

-- 1.2 Add a new vehicle for a user
INSERT INTO vehicle (user_id, vehicle_number, vehicle_type, brand, model, battery_capacity)
VALUES (1, 'MH01XY9999', 'Sedan', 'Tata', 'Nexon EV', 40.50);

-- 1.3 Add a new charging station
INSERT INTO charging_station (station_name, address, contact_number, number_of_chargers, operating_hours, status)
VALUES ('New Station - Bandra', 'Linking Road, Bandra West, Mumbai', '022-40005555', 3, '06:00 AM - 11:00 PM', 'Active');

-- 1.4 Add a new charger to a station
INSERT INTO charger (station_id, charger_type, power_rating, price_per_kwh, status)
VALUES (1, 'DC Fast', 50.00, 9.00, 'Available');

-- 1.5 Create a new charging session
INSERT INTO charging_session (user_id, vehicle_id, charger_id, start_time, status)
VALUES (1, 1, 1, NOW(), 'Active');

-- 1.6 Record a payment for a session
INSERT INTO payment (session_id, payment_date, amount, payment_method, payment_status)
VALUES (1, CURDATE(), 101.75, 'UPI', 'Completed');

-- 1.7 Add a staff member to a station (triggers auto-insertion into expenses)
INSERT INTO staff (station_id, full_name, role, phone, email, joining_date, salary)
VALUES (1, 'Rajesh Kumar', 'Technician', '9876500001', 'rajesh@greenvolt.com', CURDATE(), 30000.00);

-- 1.8 Add a maintenance record
INSERT INTO maintenance (charger_id, staff_id, maintenance_date, issue_description, maintenance_type, cost, status)
VALUES (1, 1, CURDATE(), 'Routine inspection', 'Preventive', 500.00, 'Scheduled');

-- 1.9 Record an expense
INSERT INTO expenses (station_id, expense_date, amount, expense_type, description)
VALUES (1, CURDATE(), 45000.00, 'Salary', 'December salary - Andheri station staff');

-- 1.10 Record revenue
INSERT INTO revenue (station_id, revenue_date, amount, source, description)
VALUES (1, CURDATE(), 25000.00, 'Charging Session', 'December charging revenue - Andheri station');

-- 1.11 Add a collaboration
INSERT INTO collaborations (station_id, partner_name, collaboration_type, contact_person, contact_number, start_date, agreed_amount, status)
VALUES (1, 'Coca-Cola India', 'Advertisement Board', 'Priya Singh', '9900009999', CURDATE(), 7500.00, 'Active');


-- ============================================================
-- SECTION 2: SELECT QUERIES (Viewing Records)
-- ============================================================

-- 2.1 Display all users with their account status
SELECT user_id, full_name, phone, email, account_status, created_at
FROM user
ORDER BY user_id;

-- 2.2 Display all vehicles with owner name
SELECT v.vehicle_id, u.full_name AS owner, v.vehicle_number, v.brand, v.model,
       v.vehicle_type, v.battery_capacity
FROM vehicle v
JOIN user u ON v.user_id = u.user_id
ORDER BY v.vehicle_id;

-- 2.3 Display all chargers with station name
SELECT c.charger_id, cs.station_name, c.charger_type, c.power_rating,
       c.price_per_kwh, c.status
FROM charger c
JOIN charging_station cs ON c.station_id = cs.station_id
ORDER BY c.charger_id;

-- 2.4 Display all charging sessions with user, vehicle, and charger info
SELECT cs.session_id, u.full_name AS user_name, v.vehicle_number,
       c.charger_id, cs.start_time, cs.end_time,
       cs.energy_consumed, cs.total_amount, cs.status
FROM charging_session cs
JOIN user u     ON cs.user_id    = u.user_id
JOIN vehicle v  ON cs.vehicle_id = v.vehicle_id
JOIN charger c  ON cs.charger_id = c.charger_id
ORDER BY cs.session_id DESC;

-- 2.5 Display all payments with session info
SELECT p.payment_id, p.session_id, u.full_name AS user_name,
       p.payment_date, p.amount, p.payment_method, p.payment_status
FROM payment p
JOIN charging_session cs ON p.session_id = cs.session_id
JOIN user u              ON cs.user_id   = u.user_id
ORDER BY p.payment_id DESC;

-- 2.6 Display all staff with station name and salary
SELECT s.staff_id, cs.station_name, s.full_name, s.role, s.phone, s.email, s.joining_date, s.salary
FROM staff s
JOIN charging_station cs ON s.station_id = cs.station_id
ORDER BY s.staff_id;

-- 2.7 Display maintenance history with charger and staff info
SELECT m.maintenance_id, c.charger_id, cs.station_name,
       st.full_name AS technician, m.maintenance_date,
       m.maintenance_type, m.issue_description, m.cost, m.status
FROM maintenance m
JOIN charger c          ON m.charger_id = c.charger_id
JOIN charging_station cs ON c.station_id = cs.station_id
JOIN staff st            ON m.staff_id   = st.staff_id
ORDER BY m.maintenance_date DESC;

-- 2.8 Display all expenses with station name
SELECT e.expense_id, cs.station_name, e.expense_date,
       e.expense_type, e.amount, e.description
FROM expenses e
JOIN charging_station cs ON e.station_id = cs.station_id
ORDER BY e.expense_date DESC;

-- 2.9 Display all revenue records with station name
SELECT r.revenue_id, cs.station_name, r.revenue_date,
       r.source, r.amount, r.description
FROM revenue r
JOIN charging_station cs ON r.station_id = cs.station_id
ORDER BY r.revenue_date DESC;

-- 2.10 Display all collaborations with station name
SELECT col.collaboration_id, cs.station_name, col.partner_name,
       col.collaboration_type, col.contact_person, col.contact_number,
       col.start_date, col.end_date, col.agreed_amount, col.status
FROM collaborations col
JOIN charging_station cs ON col.station_id = cs.station_id
ORDER BY col.start_date DESC;


-- ============================================================
-- SECTION 3: AGGREGATE QUERIES (Reports & Analytics)
-- ============================================================

-- 3.1 Total revenue across all stations
SELECT SUM(amount) AS total_revenue FROM revenue;

-- 3.2 Total expenses across all stations
SELECT SUM(amount) AS total_expenses FROM expenses;

-- 3.3 Estimated profit (Total Revenue - Total Expenses)
SELECT
    (SELECT COALESCE(SUM(amount), 0) FROM revenue)  AS total_revenue,
    (SELECT COALESCE(SUM(amount), 0) FROM expenses) AS total_expenses,
    (SELECT COALESCE(SUM(amount), 0) FROM revenue) -
    (SELECT COALESCE(SUM(amount), 0) FROM expenses) AS estimated_profit;

-- 3.4 Revenue by source (grouped)
SELECT source, SUM(amount) AS total_revenue, COUNT(*) AS records
FROM revenue
GROUP BY source
ORDER BY total_revenue DESC;

-- 3.5 Expenses by type (grouped)
SELECT expense_type, SUM(amount) AS total_expenses, COUNT(*) AS records
FROM expenses
GROUP BY expense_type
ORDER BY total_expenses DESC;

-- 3.6 Station-wise total revenue
SELECT cs.station_name, COALESCE(SUM(r.amount), 0) AS total_revenue
FROM charging_station cs
LEFT JOIN revenue r ON cs.station_id = r.station_id
GROUP BY cs.station_id, cs.station_name
ORDER BY total_revenue DESC;

-- 3.7 Station-wise total expenses
SELECT cs.station_name, COALESCE(SUM(e.amount), 0) AS total_expenses
FROM charging_station cs
LEFT JOIN expenses e ON cs.station_id = e.station_id
GROUP BY cs.station_id, cs.station_name
ORDER BY total_expenses DESC;

-- 3.8 Count of users, vehicles, stations, chargers
SELECT
    (SELECT COUNT(*) FROM user)             AS total_users,
    (SELECT COUNT(*) FROM vehicle)          AS total_vehicles,
    (SELECT COUNT(*) FROM charging_station) AS total_stations,
    (SELECT COUNT(*) FROM charger)          AS total_chargers;

-- 3.9 Find active chargers
SELECT c.charger_id, cs.station_name, c.charger_type, c.power_rating, c.status
FROM charger c
JOIN charging_station cs ON c.station_id = cs.station_id
WHERE c.status = 'Available'
ORDER BY cs.station_id;

-- 3.10 Find active charging sessions
SELECT cs.session_id, u.full_name AS user_name, v.vehicle_number,
       c.charger_id, cs.start_time
FROM charging_session cs
JOIN user u    ON cs.user_id    = u.user_id
JOIN vehicle v ON cs.vehicle_id = v.vehicle_id
JOIN charger c ON cs.charger_id = c.charger_id
WHERE cs.status = 'Active'
ORDER BY cs.start_time;

-- 3.11 Charger status distribution
SELECT status, COUNT(*) AS count
FROM charger
GROUP BY status;

-- 3.12 Session status distribution
SELECT status, COUNT(*) AS count
FROM charging_session
GROUP BY status;

-- 3.13 Average energy consumed per completed session
SELECT AVG(energy_consumed) AS avg_energy_kwh
FROM charging_session
WHERE status = 'Completed' AND energy_consumed IS NOT NULL;

-- 3.14 Total energy consumed per station (via charger)
SELECT cs.station_name, COALESCE(SUM(s.energy_consumed), 0) AS total_energy_kwh
FROM charging_station cs
JOIN charger c          ON cs.station_id = c.station_id
LEFT JOIN charging_session s ON c.charger_id = s.charger_id
GROUP BY cs.station_id, cs.station_name;

-- 3.15 Maintenance cost summary by status
SELECT status, SUM(cost) AS total_cost, COUNT(*) AS records
FROM maintenance
GROUP BY status;


-- ============================================================
-- SECTION 4: UPDATE QUERIES
-- ============================================================

-- 4.1 Update user account status
UPDATE user SET account_status = 'Suspended' WHERE user_id = 5;

-- 4.2 Update charger status to available after maintenance
UPDATE charger SET status = 'Available' WHERE charger_id = 4;

-- 4.3 Complete a charging session
UPDATE charging_session
SET end_time = NOW(), energy_consumed = 20.50, total_amount = 184.50, status = 'Completed'
WHERE session_id = 5;

-- 4.4 Update payment status
UPDATE payment SET payment_status = 'Completed' WHERE payment_id = 1;

-- 4.5 Update collaboration status to expired
UPDATE collaborations SET status = 'Expired' WHERE collaboration_id = 4;


-- ============================================================
-- SECTION 5: DELETE QUERIES (with FK consideration)
-- ============================================================

-- 5.1 Delete a collaboration (no child dependencies)
DELETE FROM collaborations WHERE collaboration_id = 4;

-- 5.2 Delete a maintenance record
DELETE FROM maintenance WHERE maintenance_id = 4;

-- 5.3 Delete an expense record
DELETE FROM expenses WHERE expense_id = 10;

-- 5.4 Delete a revenue record
DELETE FROM revenue WHERE revenue_id = 7;

-- NOTE: Foreign key constraints in schema.sql are configured with ON DELETE CASCADE,
-- so deleting a user automatically deletes their vehicles & sessions, and deleting
-- a station automatically deletes its chargers, staff, expenses, revenue, etc.
