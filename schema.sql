-- ============================================================
-- EV Charging Station Management System
-- Database Schema
-- ============================================================

DROP DATABASE IF EXISTS ev_charging_db;
CREATE DATABASE ev_charging_db;
USE ev_charging_db;

-- ============================================================
-- TABLE: admin
-- Stores administrator login credentials
-- ============================================================
CREATE TABLE IF NOT EXISTS admin (
    admin_id      INT AUTO_INCREMENT PRIMARY KEY,
    full_name     VARCHAR(100) NOT NULL,
    email         VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL
);

-- ============================================================
-- TABLE: user
-- Stores registered EV users
-- ============================================================
CREATE TABLE IF NOT EXISTS user (
    user_id        INT AUTO_INCREMENT PRIMARY KEY,
    full_name      VARCHAR(100) NOT NULL,
    phone          VARCHAR(20)  NOT NULL,
    email          VARCHAR(100) NOT NULL UNIQUE,
    password_hash  VARCHAR(255) NOT NULL,
    address        TEXT,
    account_status ENUM('Active', 'Inactive', 'Suspended') NOT NULL DEFAULT 'Active',
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE: vehicle
-- Stores vehicles owned by users
-- ============================================================
CREATE TABLE IF NOT EXISTS vehicle (
    vehicle_id       INT AUTO_INCREMENT PRIMARY KEY,
    user_id          INT          NOT NULL,
    vehicle_number   VARCHAR(20)  NOT NULL UNIQUE,
    vehicle_type     VARCHAR(50)  NOT NULL,
    brand            VARCHAR(50)  NOT NULL,
    model            VARCHAR(50)  NOT NULL,
    battery_capacity DECIMAL(8,2) NOT NULL CHECK (battery_capacity > 0),
    CONSTRAINT fk_vehicle_user FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE: charging_station
-- Stores EV charging station details
-- ============================================================
CREATE TABLE IF NOT EXISTS charging_station (
    station_id        INT AUTO_INCREMENT PRIMARY KEY,
    station_name      VARCHAR(100) NOT NULL,
    address           TEXT         NOT NULL,
    contact_number    VARCHAR(20),
    number_of_chargers INT         DEFAULT 0,
    operating_hours   VARCHAR(100),
    status            ENUM('Active', 'Inactive', 'Under Maintenance') NOT NULL DEFAULT 'Active'
);

-- ============================================================
-- TABLE: charger
-- Stores individual chargers belonging to stations
-- ============================================================
CREATE TABLE IF NOT EXISTS charger (
    charger_id    INT AUTO_INCREMENT PRIMARY KEY,
    station_id    INT          NOT NULL,
    charger_type  VARCHAR(50)  NOT NULL,
    power_rating  DECIMAL(8,2) NOT NULL CHECK (power_rating > 0),
    price_per_kwh DECIMAL(8,2) NOT NULL CHECK (price_per_kwh > 0),
    status        ENUM('Available', 'In Use', 'Under Maintenance', 'Inactive') NOT NULL DEFAULT 'Available',
    CONSTRAINT fk_charger_station FOREIGN KEY (station_id) REFERENCES charging_station(station_id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE: charging_session
-- Stores individual EV charging sessions
-- ============================================================
CREATE TABLE IF NOT EXISTS charging_session (
    session_id      INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT          NOT NULL,
    vehicle_id      INT          NOT NULL,
    charger_id      INT          NOT NULL,
    start_time      DATETIME     NOT NULL,
    end_time        DATETIME,
    energy_consumed DECIMAL(8,2) CHECK (energy_consumed >= 0),
    total_amount    DECIMAL(10,2) CHECK (total_amount >= 0),
    status          ENUM('Active', 'Completed', 'Cancelled') NOT NULL DEFAULT 'Active',
    CONSTRAINT fk_session_user    FOREIGN KEY (user_id)    REFERENCES user(user_id)    ON DELETE CASCADE,
    CONSTRAINT fk_session_vehicle FOREIGN KEY (vehicle_id) REFERENCES vehicle(vehicle_id) ON DELETE CASCADE,
    CONSTRAINT fk_session_charger FOREIGN KEY (charger_id) REFERENCES charger(charger_id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE: payment
-- Stores payment for each charging session (1:1 with session)
-- ============================================================
CREATE TABLE IF NOT EXISTS payment (
    payment_id     INT AUTO_INCREMENT PRIMARY KEY,
    session_id     INT          NOT NULL UNIQUE,
    payment_date   DATE         NOT NULL,
    amount         DECIMAL(10,2) NOT NULL CHECK (amount > 0),
    payment_method ENUM('Cash', 'Card', 'UPI', 'Net Banking', 'Wallet') NOT NULL,
    payment_status ENUM('Pending', 'Completed', 'Failed', 'Refunded') NOT NULL DEFAULT 'Pending',
    CONSTRAINT fk_payment_session FOREIGN KEY (session_id) REFERENCES charging_session(session_id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE: staff
-- Stores staff members assigned to stations
-- ============================================================
CREATE TABLE IF NOT EXISTS staff (
    staff_id     INT AUTO_INCREMENT PRIMARY KEY,
    station_id   INT          NOT NULL,
    full_name    VARCHAR(100) NOT NULL,
    role         ENUM('Admin', 'Manager', 'Technician', 'Accountant', 'Attendant', 'Other') NOT NULL,
    phone        VARCHAR(20),
    email        VARCHAR(100),
    joining_date DATE         NOT NULL,
    salary       DECIMAL(10,2) NOT NULL DEFAULT 25000.00 CHECK (salary > 0),
    CONSTRAINT fk_staff_station FOREIGN KEY (station_id) REFERENCES charging_station(station_id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE: maintenance
-- Stores maintenance records for chargers
-- ============================================================
CREATE TABLE IF NOT EXISTS maintenance (
    maintenance_id    INT AUTO_INCREMENT PRIMARY KEY,
    charger_id        INT          NOT NULL,
    staff_id          INT          NOT NULL,
    maintenance_date  DATE         NOT NULL,
    issue_description TEXT,
    maintenance_type  VARCHAR(100) NOT NULL,
    cost              DECIMAL(10,2) CHECK (cost >= 0),
    status            ENUM('Scheduled', 'In Progress', 'Completed', 'Cancelled') NOT NULL DEFAULT 'Scheduled',
    CONSTRAINT fk_maintenance_charger FOREIGN KEY (charger_id) REFERENCES charger(charger_id) ON DELETE CASCADE,
    CONSTRAINT fk_maintenance_staff   FOREIGN KEY (staff_id)   REFERENCES staff(staff_id)   ON DELETE CASCADE
);

-- ============================================================
-- TABLE: expenses
-- Stores all station expenses (salary, electricity, rent, etc.)
-- ============================================================
CREATE TABLE IF NOT EXISTS expenses (
    expense_id   INT AUTO_INCREMENT PRIMARY KEY,
    station_id   INT          NOT NULL,
    expense_date DATE         NOT NULL,
    amount       DECIMAL(10,2) NOT NULL CHECK (amount > 0),
    expense_type ENUM('Salary', 'Charger Maintenance', 'Station Maintenance',
                      'Electricity', 'Rent', 'Equipment', 'Utilities', 'Other') NOT NULL,
    description  TEXT,
    CONSTRAINT fk_expenses_station FOREIGN KEY (station_id) REFERENCES charging_station(station_id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE: revenue
-- Stores all station income (charging, ads, rentals, etc.)
-- ============================================================
CREATE TABLE IF NOT EXISTS revenue (
    revenue_id   INT AUTO_INCREMENT PRIMARY KEY,
    station_id   INT          NOT NULL,
    revenue_date DATE         NOT NULL,
    amount       DECIMAL(10,2) NOT NULL CHECK (amount > 0),
    source       ENUM('Charging Session', 'Advertisement', 'Land Rent',
                      'Cafe Rent', 'Convenience Store Rent', 'Other') NOT NULL,
    description  TEXT,
    CONSTRAINT fk_revenue_station FOREIGN KEY (station_id) REFERENCES charging_station(station_id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE: collaborations
-- Stores business partnership/collaboration agreements
-- ============================================================
CREATE TABLE IF NOT EXISTS collaborations (
    collaboration_id   INT AUTO_INCREMENT PRIMARY KEY,
    station_id         INT          NOT NULL,
    partner_name       VARCHAR(100) NOT NULL,
    collaboration_type ENUM('Advertisement Board', 'Land Rental', 'Cafe',
                            'Convenience Store', 'Other') NOT NULL,
    contact_person     VARCHAR(100),
    contact_number     VARCHAR(20),
    start_date         DATE NOT NULL,
    end_date           DATE,
    agreed_amount      DECIMAL(10,2) CHECK (agreed_amount >= 0),
    status             ENUM('Active', 'Expired', 'Terminated', 'Pending') NOT NULL DEFAULT 'Active',
    description        TEXT,
    CONSTRAINT fk_collab_station FOREIGN KEY (station_id) REFERENCES charging_station(station_id) ON DELETE CASCADE
);

-- ============================================================
-- AUTOMATED TRIGGERS FOR REAL-TIME FINANCIAL & OPERATIONAL SYNC
-- ============================================================

-- 1. Auto-log Staff Salary to Expenses
DROP TRIGGER IF EXISTS trg_staff_insert_salary_expense;
DELIMITER //
CREATE TRIGGER trg_staff_insert_salary_expense
AFTER INSERT ON staff
FOR EACH ROW
BEGIN
    IF NEW.salary IS NOT NULL AND NEW.salary > 0 THEN
        INSERT INTO expenses (station_id, expense_date, amount, expense_type, description)
        VALUES (NEW.station_id, NEW.joining_date, NEW.salary, 'Salary', CONCAT('Monthly salary for ', NEW.full_name, ' (', NEW.role, ')'));
    END IF;
END; //
DELIMITER ;

-- 2. Auto-log Maintenance Cost to Expenses
DROP TRIGGER IF EXISTS trg_maintenance_insert_expense;
DELIMITER //
CREATE TRIGGER trg_maintenance_insert_expense
AFTER INSERT ON maintenance
FOR EACH ROW
BEGIN
    DECLARE st_id INT;
    IF NEW.cost IS NOT NULL AND NEW.cost > 0 THEN
        SELECT station_id INTO st_id FROM charger WHERE charger_id = NEW.charger_id;
        IF st_id IS NOT NULL THEN
            INSERT INTO expenses (station_id, expense_date, amount, expense_type, description)
            VALUES (st_id, NEW.maintenance_date, NEW.cost, 'Charger Maintenance', CONCAT('Maintenance cost for Charger #', NEW.charger_id, ' - ', NEW.maintenance_type));
        END IF;
    END IF;
END; //
DELIMITER ;

-- 3. Auto-log Completed Payment to Revenue
DROP TRIGGER IF EXISTS trg_payment_insert_revenue;
DELIMITER //
CREATE TRIGGER trg_payment_insert_revenue
AFTER INSERT ON payment
FOR EACH ROW
BEGIN
    DECLARE st_id INT;
    IF NEW.payment_status = 'Completed' AND NEW.amount > 0 THEN
        SELECT c.station_id INTO st_id
        FROM charging_session cs
        JOIN charger c ON cs.charger_id = c.charger_id
        WHERE cs.session_id = NEW.session_id;
        IF st_id IS NOT NULL THEN
            INSERT INTO revenue (station_id, revenue_date, amount, source, description)
            VALUES (st_id, NEW.payment_date, NEW.amount, 'Charging Session', CONCAT('Payment received for Charging Session #', NEW.session_id));
        END IF;
    END IF;
END; //
DELIMITER ;

-- 4. Auto-log Collaboration to Revenue
DROP TRIGGER IF EXISTS trg_collab_insert_revenue;
DELIMITER //
CREATE TRIGGER trg_collab_insert_revenue
AFTER INSERT ON collaborations
FOR EACH ROW
BEGIN
    DECLARE rev_source VARCHAR(50);
    IF NEW.status = 'Active' AND NEW.agreed_amount IS NOT NULL AND NEW.agreed_amount > 0 THEN
        IF NEW.collaboration_type = 'Advertisement Board' THEN SET rev_source = 'Advertisement';
        ELSEIF NEW.collaboration_type = 'Land Rental' THEN SET rev_source = 'Land Rent';
        ELSEIF NEW.collaboration_type = 'Cafe' THEN SET rev_source = 'Cafe Rent';
        ELSEIF NEW.collaboration_type = 'Convenience Store' THEN SET rev_source = 'Convenience Store Rent';
        ELSE SET rev_source = 'Other';
        END IF;

        INSERT INTO revenue (station_id, revenue_date, amount, source, description)
        VALUES (NEW.station_id, NEW.start_date, NEW.agreed_amount, rev_source, CONCAT('Collaboration revenue from ', NEW.partner_name));
    END IF;
END; //
DELIMITER ;

-- 5. Auto-update Charger Count on Station
DROP TRIGGER IF EXISTS trg_update_charger_count_insert;
DROP TRIGGER IF EXISTS trg_update_charger_count_delete;
DELIMITER //
CREATE TRIGGER trg_update_charger_count_insert
AFTER INSERT ON charger
FOR EACH ROW
BEGIN
    UPDATE charging_station
    SET number_of_chargers = (SELECT COUNT(*) FROM charger WHERE station_id = NEW.station_id)
    WHERE station_id = NEW.station_id;
END; //

CREATE TRIGGER trg_update_charger_count_delete
AFTER DELETE ON charger
FOR EACH ROW
BEGIN
    UPDATE charging_station
    SET number_of_chargers = (SELECT COUNT(*) FROM charger WHERE station_id = OLD.station_id)
    WHERE station_id = OLD.station_id;
END; //
DELIMITER ;

-- 6. Auto-toggle Charger Status on Session Create/Update
DROP TRIGGER IF EXISTS trg_session_charger_status;
DROP TRIGGER IF EXISTS trg_session_charger_status_update;
DELIMITER //
CREATE TRIGGER trg_session_charger_status
AFTER INSERT ON charging_session
FOR EACH ROW
BEGIN
    IF NEW.status = 'Active' THEN
        UPDATE charger SET status = 'In Use' WHERE charger_id = NEW.charger_id;
    END IF;
END; //

CREATE TRIGGER trg_session_charger_status_update
AFTER UPDATE ON charging_session
FOR EACH ROW
BEGIN
    IF NEW.status = 'Completed' OR NEW.status = 'Cancelled' THEN
        UPDATE charger SET status = 'Available' WHERE charger_id = NEW.charger_id;
    ELSEIF NEW.status = 'Active' THEN
        UPDATE charger SET status = 'In Use' WHERE charger_id = NEW.charger_id;
    END IF;
END; //
DELIMITER ;

-- 7. Auto-toggle Charger Status on Maintenance Create/Update
DROP TRIGGER IF EXISTS trg_maint_charger_status;
DROP TRIGGER IF EXISTS trg_maint_charger_status_update;
DELIMITER //
CREATE TRIGGER trg_maint_charger_status
AFTER INSERT ON maintenance
FOR EACH ROW
BEGIN
    IF NEW.status IN ('Scheduled', 'In Progress') THEN
        UPDATE charger SET status = 'Under Maintenance' WHERE charger_id = NEW.charger_id;
    END IF;
END; //

CREATE TRIGGER trg_maint_charger_status_update
AFTER UPDATE ON maintenance
FOR EACH ROW
BEGIN
    IF NEW.status = 'Completed' OR NEW.status = 'Cancelled' THEN
        UPDATE charger SET status = 'Available' WHERE charger_id = NEW.charger_id;
    ELSEIF NEW.status IN ('Scheduled', 'In Progress') THEN
        UPDATE charger SET status = 'Under Maintenance' WHERE charger_id = NEW.charger_id;
    END IF;
END; //
DELIMITER ;
