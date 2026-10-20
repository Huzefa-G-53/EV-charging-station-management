from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from routes.auth_routes import customer_required
from database.db_connection import execute_query
import mysql.connector
from datetime import datetime

customer_bp = Blueprint('customer', __name__, url_prefix='/customer')


# ── Dashboard ─────────────────────────────────────────────────────────────────
@customer_bp.route('/dashboard')
@customer_required
def dashboard():
    user_id = session['user_id']
    user = execute_query('SELECT * FROM user WHERE user_id = %s', (user_id,), fetchone=True)

    # User vehicles
    vehicles = execute_query(
        'SELECT * FROM vehicle WHERE user_id = %s ORDER BY vehicle_id',
        (user_id,), fetch=True
    )

    # Active session check
    active_session = execute_query(
        '''SELECT cs.*, c.charger_type, c.power_rating, c.price_per_kwh,
                  st.station_name, st.address AS station_address, v.vehicle_number, v.model
           FROM charging_session cs
           JOIN charger c ON cs.charger_id = c.charger_id
           JOIN charging_station st ON c.station_id = st.station_id
           JOIN vehicle v ON cs.vehicle_id = v.vehicle_id
           WHERE cs.user_id = %s AND cs.status = 'Active'
           ORDER BY cs.session_id DESC LIMIT 1''',
        (user_id,), fetchone=True
    )

    # Stats
    stats = execute_query(
        '''SELECT
             COUNT(*) AS total_sessions,
             COALESCE(SUM(energy_consumed), 0) AS total_kwh,
             COALESCE(SUM(total_amount), 0) AS total_spent
           FROM charging_session
           WHERE user_id = %s AND status = 'Completed' ''',
        (user_id,), fetchone=True
    )

    # Recent completed sessions for table
    recent_sessions = execute_query(
        '''SELECT cs.*, c.charger_type, st.station_name, v.vehicle_number, p.payment_status
           FROM charging_session cs
           JOIN charger c ON cs.charger_id = c.charger_id
           JOIN charging_station st ON c.station_id = st.station_id
           JOIN vehicle v ON cs.vehicle_id = v.vehicle_id
           LEFT JOIN payment p ON cs.session_id = p.session_id
           WHERE cs.user_id = %s
           ORDER BY cs.session_id DESC LIMIT 5''',
        (user_id,), fetch=True
    )

    # Driver session history for trend chart (chronological)
    trend_data = execute_query(
        '''SELECT cs.session_id, cs.start_time,
                  COALESCE(cs.energy_consumed, 0) AS kwh,
                  COALESCE(cs.total_amount, 0) AS amount
           FROM charging_session cs
           WHERE cs.user_id = %s AND cs.status = 'Completed'
           ORDER BY cs.start_time ASC
           LIMIT 8''',
        (user_id,), fetch=True
    )

    # Station visits breakdown
    station_visits = execute_query(
        '''SELECT st.station_name, COUNT(*) AS visits
           FROM charging_session cs
           JOIN charger c ON cs.charger_id = c.charger_id
           JOIN charging_station st ON c.station_id = st.station_id
           WHERE cs.user_id = %s
           GROUP BY st.station_id, st.station_name
           ORDER BY visits DESC''',
        (user_id,), fetch=True
    )

    # Eco impact calculations (1 kWh = ~0.82 kg CO2 offset)
    total_kwh = float(stats['total_kwh'] or 0)
    co2_saved = round(total_kwh * 0.82, 1)
    trees_equiv = round(co2_saved / 21.0, 1) if co2_saved > 0 else 0

    import json
    driver_chart_payload = {
        'trend': {
            'labels': [t['start_time'].strftime('%d %b') if t['start_time'] else f'#{t["session_id"]}' for t in trend_data],
            'kwh': [float(t['kwh']) for t in trend_data],
            'amount': [float(t['amount']) for t in trend_data]
        },
        'stations': {
            'labels': [s['station_name'].replace(' EV Station', '').replace(' Charging Hub', '').replace(' Charging Station', '') for s in station_visits],
            'values': [int(s['visits']) for s in station_visits]
        }
    }

    return render_template(
        'customer/dashboard.html',
        user=user,
        vehicles=vehicles,
        active_session=active_session,
        stats=stats,
        recent_sessions=recent_sessions,
        co2_saved=co2_saved,
        trees_equiv=trees_equiv,
        driver_chart_payload_json=json.dumps(driver_chart_payload)
    )


# ── Vehicles Management ───────────────────────────────────────────────────────
@customer_bp.route('/vehicles')
@customer_required
def vehicles():
    user_id = session['user_id']
    my_vehicles = execute_query(
        'SELECT * FROM vehicle WHERE user_id = %s ORDER BY vehicle_id DESC',
        (user_id,), fetch=True
    )
    return render_template('customer/vehicles.html', vehicles=my_vehicles)


@customer_bp.route('/vehicles/add', methods=['GET', 'POST'])
@customer_required
def add_vehicle():
    user_id = session['user_id']
    if request.method == 'POST':
        vehicle_number   = request.form.get('vehicle_number', '').strip().upper()
        vehicle_type     = request.form.get('vehicle_type', '').strip()
        brand            = request.form.get('brand', '').strip()
        model            = request.form.get('model', '').strip()
        battery_capacity = request.form.get('battery_capacity', '').strip()

        if not all([vehicle_number, vehicle_type, brand, model, battery_capacity]):
            flash('All vehicle specifications are required.', 'danger')
            return render_template('customer/vehicle_form.html', vehicle=None)

        try:
            execute_query(
                '''INSERT INTO vehicle (user_id, vehicle_number, vehicle_type, brand, model, battery_capacity)
                   VALUES (%s, %s, %s, %s, %s, %s)''',
                (user_id, vehicle_number, vehicle_type, brand, model, battery_capacity)
            )
            flash('Vehicle added to your garage successfully.', 'success')
            return redirect(url_for('customer.vehicles'))
        except mysql.connector.IntegrityError:
            flash('This license plate number is already registered in the system.', 'danger')
        except Exception:
            flash('Failed to register vehicle. Please try again.', 'danger')

    return render_template('customer/vehicle_form.html', vehicle=None)


@customer_bp.route('/vehicles/<int:vehicle_id>/edit', methods=['GET', 'POST'])
@customer_required
def edit_vehicle(vehicle_id):
    user_id = session['user_id']
    vehicle = execute_query(
        'SELECT * FROM vehicle WHERE vehicle_id = %s AND user_id = %s',
        (vehicle_id, user_id), fetchone=True
    )
    if not vehicle:
        flash('Vehicle not found or unauthorized access.', 'danger')
        return redirect(url_for('customer.vehicles'))

    if request.method == 'POST':
        vehicle_number   = request.form.get('vehicle_number', '').strip().upper()
        vehicle_type     = request.form.get('vehicle_type', '').strip()
        brand            = request.form.get('brand', '').strip()
        model            = request.form.get('model', '').strip()
        battery_capacity = request.form.get('battery_capacity', '').strip()

        if not all([vehicle_number, vehicle_type, brand, model, battery_capacity]):
            flash('All vehicle fields are required.', 'danger')
            return render_template('customer/vehicle_form.html', vehicle=vehicle)

        try:
            execute_query(
                '''UPDATE vehicle SET vehicle_number=%s, vehicle_type=%s, brand=%s, model=%s, battery_capacity=%s
                   WHERE vehicle_id=%s AND user_id=%s''',
                (vehicle_number, vehicle_type, brand, model, battery_capacity, vehicle_id, user_id)
            )
            flash('Vehicle updated successfully.', 'success')
            return redirect(url_for('customer.vehicles'))
        except mysql.connector.IntegrityError:
            flash('This license plate number is already registered by another user.', 'danger')

    return render_template('customer/vehicle_form.html', vehicle=vehicle)


@customer_bp.route('/vehicles/<int:vehicle_id>/delete', methods=['POST'])
@customer_required
def delete_vehicle(vehicle_id):
    user_id = session['user_id']
    # Check if vehicle has active session
    active = execute_query(
        "SELECT session_id FROM charging_session WHERE vehicle_id = %s AND status = 'Active'",
        (vehicle_id,), fetchone=True
    )
    if active:
        flash('Cannot delete vehicle while it is in an active charging session.', 'danger')
        return redirect(url_for('customer.vehicles'))

    try:
        execute_query(
            'DELETE FROM vehicle WHERE vehicle_id = %s AND user_id = %s',
            (vehicle_id, user_id)
        )
        flash('Vehicle removed from your garage.', 'success')
    except mysql.connector.IntegrityError:
        flash('Vehicle has charging history and cannot be completely deleted.', 'danger')
    return redirect(url_for('customer.vehicles'))


# ── Stations & Charger Availability ───────────────────────────────────────────
@customer_bp.route('/stations')
@customer_required
def stations():
    all_stations = execute_query(
        '''SELECT cs.*,
                  (SELECT COUNT(*) FROM charger c WHERE c.station_id = cs.station_id AND c.status = 'Available') AS available_chargers,
                  (SELECT COUNT(*) FROM charger c WHERE c.station_id = cs.station_id) AS total_chargers
           FROM charging_station cs
           WHERE cs.status = 'Active'
           ORDER BY cs.station_id''',
        fetch=True
    )
    chargers = execute_query(
        '''SELECT c.*, cs.station_name
           FROM charger c
           JOIN charging_station cs ON c.station_id = cs.station_id
           ORDER BY c.station_id, c.charger_id''',
        fetch=True
    )
    return render_template('customer/stations.html', stations=all_stations, chargers=chargers)


# ── Charging Sessions ─────────────────────────────────────────────────────────
@customer_bp.route('/sessions')
@customer_required
def sessions():
    user_id = session['user_id']
    user_sessions = execute_query(
        '''SELECT cs.*, c.charger_type, c.power_rating, c.price_per_kwh,
                  st.station_name, v.vehicle_number, v.model,
                  p.payment_status, p.payment_id
           FROM charging_session cs
           JOIN charger c ON cs.charger_id = c.charger_id
           JOIN charging_station st ON c.station_id = st.station_id
           JOIN vehicle v ON cs.vehicle_id = v.vehicle_id
           LEFT JOIN payment p ON cs.session_id = p.session_id
           WHERE cs.user_id = %s
           ORDER BY cs.session_id DESC''',
        (user_id,), fetch=True
    )
    return render_template('customer/sessions.html', sessions=user_sessions)


@customer_bp.route('/sessions/start', methods=['GET', 'POST'])
@customer_required
def start_session():
    user_id = session['user_id']
    # Check if user already has an active session
    active = execute_query(
        "SELECT session_id FROM charging_session WHERE user_id = %s AND status = 'Active'",
        (user_id,), fetchone=True
    )
    if active:
        flash('You already have an active charging session in progress.', 'warning')
        return redirect(url_for('customer.sessions'))

    vehicles = execute_query(
        'SELECT * FROM vehicle WHERE user_id = %s ORDER BY vehicle_number',
        (user_id,), fetch=True
    )
    if not vehicles:
        flash('Please register at least one EV vehicle before starting a charging session.', 'warning')
        return redirect(url_for('customer.add_vehicle'))

    chargers = execute_query(
        '''SELECT c.*, cs.station_name, cs.address
           FROM charger c
           JOIN charging_station cs ON c.station_id = cs.station_id
           WHERE c.status = 'Available' AND cs.status = 'Active'
           ORDER BY cs.station_name, c.charger_id''',
        fetch=True
    )

    preset_charger = request.args.get('charger_id')

    if request.method == 'POST':
        vehicle_id = request.form.get('vehicle_id')
        charger_id = request.form.get('charger_id')

        if not vehicle_id or not charger_id:
            flash('Please select both a vehicle and an available charger.', 'danger')
            return render_template('customer/start_session.html', vehicles=vehicles, chargers=chargers, preset_charger=preset_charger)

        # Ensure selected vehicle belongs to user
        v_check = execute_query('SELECT vehicle_id FROM vehicle WHERE vehicle_id = %s AND user_id = %s', (vehicle_id, user_id), fetchone=True)
        if not v_check:
            flash('Invalid vehicle selection.', 'danger')
            return redirect(url_for('customer.start_session'))

        # Verify charger is Available
        c_check = execute_query("SELECT charger_id, status FROM charger WHERE charger_id = %s", (charger_id,), fetchone=True)
        if not c_check or c_check['status'] != 'Available':
            flash('Selected charger is no longer available. Please select another charger.', 'danger')
            return redirect(url_for('customer.start_session'))

        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        execute_query(
            '''INSERT INTO charging_session (user_id, vehicle_id, charger_id, start_time, status)
               VALUES (%s, %s, %s, %s, 'Active')''',
            (user_id, vehicle_id, charger_id, now_str)
        )
        flash('Charging session started! Charger is now reserved and in use.', 'success')
        return redirect(url_for('customer.dashboard'))

    return render_template('customer/start_session.html', vehicles=vehicles, chargers=chargers, preset_charger=preset_charger)


@customer_bp.route('/sessions/<int:session_id>/stop', methods=['POST'])
@customer_required
def stop_session(session_id):
    user_id = session['user_id']
    cs = execute_query(
        '''SELECT cs.*, c.price_per_kwh, v.battery_capacity
           FROM charging_session cs
           JOIN charger c ON cs.charger_id = c.charger_id
           JOIN vehicle v ON cs.vehicle_id = v.vehicle_id
           WHERE cs.session_id = %s AND cs.user_id = %s AND cs.status = 'Active' ''',
        (session_id, user_id), fetchone=True
    )
    if not cs:
        flash('Active session not found.', 'danger')
        return redirect(url_for('customer.sessions'))

    # Calculate or accept energy consumed
    energy_consumed = request.form.get('energy_consumed')
    if not energy_consumed:
        # Default estimation: 75% of battery capacity or 25 kWh
        energy_consumed = round(float(cs['battery_capacity']) * 0.70, 2)
    else:
        energy_consumed = float(energy_consumed)

    price_per_kwh = float(cs['price_per_kwh'])
    total_amount = round(energy_consumed * price_per_kwh, 2)
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    execute_query(
        '''UPDATE charging_session
           SET end_time = %s, energy_consumed = %s, total_amount = %s, status = 'Completed'
           WHERE session_id = %s''',
        (now_str, energy_consumed, total_amount, session_id)
    )

    flash(f'Charging completed! Consumed {energy_consumed} kWh. Total amount: ₹{total_amount:.2f}', 'success')
    return redirect(url_for('customer.payments'))


# ── Billing & Payments ────────────────────────────────────────────────────────
@customer_bp.route('/payments')
@customer_required
def payments():
    user_id = session['user_id']
    bills = execute_query(
        '''SELECT cs.session_id, cs.start_time, cs.end_time, cs.energy_consumed, cs.total_amount,
                  c.charger_type, st.station_name, v.vehicle_number,
                  p.payment_id, p.payment_date, p.payment_method,
                  COALESCE(p.payment_status, 'Unpaid') AS bill_status
           FROM charging_session cs
           JOIN charger c ON cs.charger_id = c.charger_id
           JOIN charging_station st ON c.station_id = st.station_id
           JOIN vehicle v ON cs.vehicle_id = v.vehicle_id
           LEFT JOIN payment p ON cs.session_id = p.session_id
           WHERE cs.user_id = %s AND cs.status = 'Completed'
           ORDER BY cs.session_id DESC''',
        (user_id,), fetch=True
    )
    return render_template('customer/payments.html', bills=bills)


@customer_bp.route('/payments/<int:session_id>/pay', methods=['POST'])
@customer_required
def pay_bill(session_id):
    user_id = session['user_id']
    cs = execute_query(
        'SELECT session_id, total_amount FROM charging_session WHERE session_id = %s AND user_id = %s',
        (session_id, user_id), fetchone=True
    )
    if not cs:
        flash('Invalid session.', 'danger')
        return redirect(url_for('customer.payments'))

    # Check if already paid
    existing = execute_query('SELECT payment_id FROM payment WHERE session_id = %s', (session_id,), fetchone=True)
    if existing:
        flash('This bill is already paid.', 'info')
        return redirect(url_for('customer.payments'))

    payment_method = request.form.get('payment_method', 'UPI')
    amount = cs['total_amount']
    today = datetime.now().strftime('%Y-%m-%d')

    execute_query(
        '''INSERT INTO payment (session_id, payment_date, amount, payment_method, payment_status)
           VALUES (%s, %s, %s, %s, 'Completed')''',
        (session_id, today, amount, payment_method)
    )
    flash(f'Payment of ₹{amount:.2f} via {payment_method} successful! Receipt generated.', 'success')
    return redirect(url_for('customer.payments'))


# ── Customer Profile, Password & Self-Deletion ────────────────────────────────
@customer_bp.route('/profile', methods=['GET', 'POST'])
@customer_required
def profile():
    user_id = session['user_id']
    user = execute_query('SELECT * FROM user WHERE user_id = %s', (user_id,), fetchone=True)

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        phone     = request.form.get('phone', '').strip()
        address   = request.form.get('address', '').strip()

        if not full_name or not phone:
            flash('Name and phone number are required.', 'danger')
            return render_template('customer/profile.html', user=user)

        execute_query(
            'UPDATE user SET full_name = %s, phone = %s, address = %s WHERE user_id = %s',
            (full_name, phone, address, user_id)
        )
        session['user_name'] = full_name
        flash('Your profile has been updated.', 'success')
        return redirect(url_for('customer.profile'))

    return render_template('customer/profile.html', user=user)


@customer_bp.route('/profile/change-password', methods=['POST'])
@customer_required
def change_password():
    user_id = session['user_id']
    current_password = request.form.get('current_password', '')
    new_password     = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')

    user = execute_query('SELECT password_hash FROM user WHERE user_id = %s', (user_id,), fetchone=True)

    if not check_password_hash(user['password_hash'], current_password):
        flash('Current password incorrect.', 'danger')
        return redirect(url_for('customer.profile'))

    if len(new_password) < 6:
        flash('New password must be at least 6 characters long.', 'danger')
        return redirect(url_for('customer.profile'))

    if new_password != confirm_password:
        flash('New passwords do not match.', 'danger')
        return redirect(url_for('customer.profile'))

    new_hash = generate_password_hash(new_password)
    execute_query('UPDATE user SET password_hash = %s WHERE user_id = %s', (new_hash, user_id))
    flash('Your password has been changed successfully.', 'success')
    return redirect(url_for('customer.profile'))


@customer_bp.route('/profile/delete-account', methods=['POST'])
@customer_required
def delete_account():
    user_id = session['user_id']
    confirm_text = request.form.get('confirm_delete', '').strip()

    if confirm_text != 'DELETE':
        flash('Please type "DELETE" exactly to confirm account removal.', 'warning')
        return redirect(url_for('customer.profile'))

    # Check for active sessions
    active = execute_query("SELECT session_id FROM charging_session WHERE user_id = %s AND status = 'Active'", (user_id,), fetchone=True)
    if active:
        flash('Cannot delete account while you have an active charging session.', 'danger')
        return redirect(url_for('customer.profile'))

    # Option 1: Soft Account Closure (Preserves authentic name on past invoices for tax/audit compliance)
    try:
        # 1. Remove registered vehicles from garage
        execute_query('DELETE FROM vehicle WHERE user_id = %s', (user_id,))

        # 2. Deactivate account, wipe credentials, keep authentic name on past billing records
        execute_query(
            '''UPDATE user 
               SET account_status = 'Inactive',
                   suspension_reason = 'Account closed by driver',
                   password_hash = 'ACCOUNT_CLOSED'
               WHERE user_id = %s''',
            (user_id,)
        )

        session.clear()
        flash('Your account has been closed and deactivated. Past invoices remain preserved for billing compliance.', 'info')
        return redirect(url_for('auth.login'))
    except Exception:
        flash('Unable to process account deactivation at this time. Please contact support.', 'danger')
        return redirect(url_for('customer.profile'))
