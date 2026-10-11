from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth_routes import login_required
from database.db_connection import execute_query
import mysql.connector

staff_bp = Blueprint('staff', __name__, url_prefix='/staff')


@staff_bp.route('/')
@login_required
def list_staff():
    station_filter = request.args.get('station_id', '')
    stations = execute_query('SELECT station_id, station_name FROM charging_station ORDER BY station_name', fetch=True)

    if station_filter:
        staff = execute_query(
            '''SELECT s.*, cs.station_name FROM staff s
               JOIN charging_station cs ON s.station_id = cs.station_id
               WHERE s.station_id = %s ORDER BY s.staff_id''',
            (station_filter,), fetch=True
        )
    else:
        staff = execute_query(
            '''SELECT s.*, cs.station_name FROM staff s
               JOIN charging_station cs ON s.station_id = cs.station_id
               ORDER BY s.staff_id''',
            fetch=True
        )
    return render_template('staff_list.html', staff=staff, stations=stations, station_filter=station_filter)


@staff_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_staff():
    stations = execute_query('SELECT station_id, station_name FROM charging_station ORDER BY station_name', fetch=True)

    if request.method == 'POST':
        station_id   = request.form.get('station_id')
        full_name    = request.form.get('full_name', '').strip()
        role         = request.form.get('role')
        phone        = request.form.get('phone', '').strip()
        email        = request.form.get('email', '').strip()
        joining_date = request.form.get('joining_date')
        salary       = request.form.get('salary', '25000.00')

        if not all([station_id, full_name, role, joining_date, salary]):
            flash('Station, name, role, joining date, and salary are required.', 'danger')
            return render_template('staff_form.html', staff=None, stations=stations)

        execute_query(
            'INSERT INTO staff (station_id, full_name, role, phone, email, joining_date, salary) VALUES (%s,%s,%s,%s,%s,%s,%s)',
            (station_id, full_name, role, phone, email, joining_date, salary)
        )
        flash('Staff member added successfully. Salary expense automatically logged.', 'success')
        return redirect(url_for('staff.list_staff'))

    return render_template('staff_form.html', staff=None, stations=stations)


@staff_bp.route('/<int:staff_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_staff(staff_id):
    staff_member = execute_query('SELECT * FROM staff WHERE staff_id = %s', (staff_id,), fetchone=True)
    stations     = execute_query('SELECT station_id, station_name FROM charging_station ORDER BY station_name', fetch=True)

    if not staff_member:
        flash('Staff member not found.', 'danger')
        return redirect(url_for('staff.list_staff'))

    if request.method == 'POST':
        station_id   = request.form.get('station_id')
        full_name    = request.form.get('full_name', '').strip()
        role         = request.form.get('role')
        phone        = request.form.get('phone', '').strip()
        email        = request.form.get('email', '').strip()
        joining_date = request.form.get('joining_date')
        salary       = request.form.get('salary', '25000.00')

        execute_query(
            'UPDATE staff SET station_id=%s, full_name=%s, role=%s, phone=%s, email=%s, joining_date=%s, salary=%s WHERE staff_id=%s',
            (station_id, full_name, role, phone, email, joining_date, salary, staff_id)
        )
        flash('Staff member updated successfully.', 'success')
        return redirect(url_for('staff.list_staff'))

    return render_template('staff_form.html', staff=staff_member, stations=stations)


@staff_bp.route('/<int:staff_id>/delete', methods=['POST'])
@login_required
def delete_staff(staff_id):
    staff_member = execute_query('SELECT full_name, role FROM staff WHERE staff_id = %s', (staff_id,), fetchone=True)
    if not staff_member:
        flash('Staff member not found.', 'danger')
        return redirect(url_for('staff.list_staff'))

    reason = request.form.get('deletion_reason', '').strip()
    if not reason:
        flash('A mandatory offboarding/deletion reason must be provided to delete an employee.', 'danger')
        return redirect(url_for('staff.list_staff'))

    try:
        execute_query('DELETE FROM staff WHERE staff_id = %s', (staff_id,))
        flash(f"Staff member {staff_member['full_name']} ({staff_member['role']}) offboarded. Reason: {reason}", 'success')
    except mysql.connector.IntegrityError:
        flash('Cannot delete: this staff member is assigned to historical maintenance logs. Please reassign those records first.', 'danger')
    except Exception:
        flash('Error removing staff member.', 'danger')
    return redirect(url_for('staff.list_staff'))
