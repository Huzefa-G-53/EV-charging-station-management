from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth_routes import login_required
from database.db_connection import execute_query
import mysql.connector

sessions_bp = Blueprint('sessions', __name__, url_prefix='/sessions')


@sessions_bp.route('/')
@login_required
def list_sessions():
    status_filter = request.args.get('status', '')
    if status_filter:
        sessions = execute_query(
            '''SELECT cs.*, u.full_name AS user_name, v.vehicle_number,
                      c.charger_type, st.station_name
               FROM charging_session cs
               JOIN user u              ON cs.user_id    = u.user_id
               JOIN vehicle v           ON cs.vehicle_id = v.vehicle_id
               JOIN charger c           ON cs.charger_id = c.charger_id
               JOIN charging_station st ON c.station_id  = st.station_id
               WHERE cs.status = %s
               ORDER BY cs.session_id DESC''',
            (status_filter,), fetch=True
        )
    else:
        sessions = execute_query(
            '''SELECT cs.*, u.full_name AS user_name, v.vehicle_number,
                      c.charger_type, st.station_name
               FROM charging_session cs
               JOIN user u              ON cs.user_id    = u.user_id
               JOIN vehicle v           ON cs.vehicle_id = v.vehicle_id
               JOIN charger c           ON cs.charger_id = c.charger_id
               JOIN charging_station st ON c.station_id  = st.station_id
               ORDER BY cs.session_id DESC''',
            fetch=True
        )
    return render_template('sessions_list.html', sessions=sessions, status_filter=status_filter)


@sessions_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_session():
    users    = execute_query("SELECT user_id, full_name FROM user WHERE account_status='Active' ORDER BY full_name", fetch=True)
    vehicles = execute_query('SELECT vehicle_id, vehicle_number, brand, model FROM vehicle ORDER BY vehicle_number', fetch=True)
    chargers = execute_query(
        "SELECT c.charger_id, c.charger_type, c.power_rating, cs.station_name FROM charger c JOIN charging_station cs ON c.station_id=cs.station_id WHERE c.status='Available' ORDER BY cs.station_name",
        fetch=True
    )

    if request.method == 'POST':
        user_id    = request.form.get('user_id')
        vehicle_id = request.form.get('vehicle_id')
        charger_id = request.form.get('charger_id')
        start_time = request.form.get('start_time')
        status     = request.form.get('status', 'Active')

        if not all([user_id, vehicle_id, charger_id, start_time]):
            flash('User, vehicle, charger, and start time are required.', 'danger')
            return render_template('sessions_form.html', session=None, users=users, vehicles=vehicles, chargers=chargers)

        # Verify charger is Available
        charger = execute_query('SELECT status, price_per_kwh FROM charger WHERE charger_id = %s', (charger_id,), fetchone=True)
        if not charger or charger['status'] != 'Available':
            flash('Selected charger is currently In Use or Under Maintenance.', 'danger')
            return render_template('sessions_form.html', session=None, users=users, vehicles=vehicles, chargers=chargers)

        execute_query(
            'INSERT INTO charging_session (user_id, vehicle_id, charger_id, start_time, status) VALUES (%s,%s,%s,%s,%s)',
            (user_id, vehicle_id, charger_id, start_time, status)
        )
        flash('Charging session created successfully.', 'success')
        return redirect(url_for('sessions.list_sessions'))

    return render_template('sessions_form.html', session=None, users=users, vehicles=vehicles, chargers=chargers)


@sessions_bp.route('/<int:session_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_session(session_id):
    session_rec = execute_query('SELECT * FROM charging_session WHERE session_id = %s', (session_id,), fetchone=True)
    if not session_rec:
        flash('Session not found.', 'danger')
        return redirect(url_for('sessions.list_sessions'))

    users    = execute_query('SELECT user_id, full_name FROM user ORDER BY full_name', fetch=True)
    vehicles = execute_query('SELECT vehicle_id, vehicle_number, brand, model FROM vehicle ORDER BY vehicle_number', fetch=True)
    chargers = execute_query(
        'SELECT c.charger_id, c.charger_type, c.power_rating, c.price_per_kwh, cs.station_name FROM charger c JOIN charging_station cs ON c.station_id=cs.station_id ORDER BY cs.station_name',
        fetch=True
    )

    if request.method == 'POST':
        user_id         = request.form.get('user_id')
        vehicle_id      = request.form.get('vehicle_id')
        charger_id      = request.form.get('charger_id')
        start_time      = request.form.get('start_time')
        end_time        = request.form.get('end_time') or None
        energy_consumed = request.form.get('energy_consumed') or None
        total_amount    = request.form.get('total_amount') or None
        status          = request.form.get('status', 'Active')

        # Auto-compute total_amount from price_per_kwh if energy_consumed is provided
        if energy_consumed and not total_amount:
            charger_info = execute_query('SELECT price_per_kwh FROM charger WHERE charger_id = %s', (charger_id,), fetchone=True)
            if charger_info:
                total_amount = round(float(energy_consumed) * float(charger_info['price_per_kwh']), 2)

        execute_query(
            '''UPDATE charging_session SET user_id=%s, vehicle_id=%s, charger_id=%s,
               start_time=%s, end_time=%s, energy_consumed=%s, total_amount=%s, status=%s
               WHERE session_id=%s''',
            (user_id, vehicle_id, charger_id, start_time, end_time, energy_consumed, total_amount, status, session_id)
        )
        flash('Session updated successfully.', 'success')
        return redirect(url_for('sessions.list_sessions'))

    return render_template('sessions_form.html', session=session_rec, users=users, vehicles=vehicles, chargers=chargers)


@sessions_bp.route('/<int:session_id>/delete', methods=['POST'])
@login_required
def delete_session(session_id):
    try:
        execute_query('DELETE FROM charging_session WHERE session_id = %s', (session_id,))
        flash('Session deleted successfully.', 'success')
    except mysql.connector.IntegrityError:
        flash('Cannot delete: this session has an associated payment record.', 'danger')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('sessions.list_sessions'))
