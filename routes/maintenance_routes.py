from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth_routes import login_required
from database.db_connection import execute_query
import mysql.connector

maintenance_bp = Blueprint('maintenance', __name__, url_prefix='/maintenance')


@maintenance_bp.route('/')
@login_required
def list_maintenance():
    status_filter = request.args.get('status', '')
    if status_filter:
        records = execute_query(
            '''SELECT m.*, c.charger_type, cs.station_name, s.full_name AS technician
               FROM maintenance m
               JOIN charger c           ON m.charger_id = c.charger_id
               JOIN charging_station cs ON c.station_id = cs.station_id
               JOIN staff s             ON m.staff_id   = s.staff_id
               WHERE m.status = %s
               ORDER BY m.maintenance_date DESC''',
            (status_filter,), fetch=True
        )
    else:
        records = execute_query(
            '''SELECT m.*, c.charger_type, cs.station_name, s.full_name AS technician
               FROM maintenance m
               JOIN charger c           ON m.charger_id = c.charger_id
               JOIN charging_station cs ON c.station_id = cs.station_id
               JOIN staff s             ON m.staff_id   = s.staff_id
               ORDER BY m.maintenance_date DESC''',
            fetch=True
        )
    return render_template('maintenance_list.html', records=records, status_filter=status_filter)


@maintenance_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_maintenance():
    chargers = execute_query(
        'SELECT c.charger_id, c.charger_type, cs.station_name FROM charger c JOIN charging_station cs ON c.station_id=cs.station_id ORDER BY cs.station_name',
        fetch=True
    )
    staff = execute_query(
        "SELECT staff_id, full_name, role FROM staff WHERE role IN ('Technician','Manager','Other') ORDER BY full_name",
        fetch=True
    )

    if request.method == 'POST':
        charger_id        = request.form.get('charger_id')
        staff_id          = request.form.get('staff_id')
        maintenance_date  = request.form.get('maintenance_date')
        issue_description = request.form.get('issue_description', '').strip()
        maintenance_type  = request.form.get('maintenance_type', '').strip()
        cost              = request.form.get('cost') or None
        status            = request.form.get('status', 'Scheduled')

        if not all([charger_id, staff_id, maintenance_date, maintenance_type]):
            flash('Charger, staff, date, and type are required.', 'danger')
            return render_template('maintenance_form.html', record=None, chargers=chargers, staff=staff)

        execute_query(
            '''INSERT INTO maintenance (charger_id, staff_id, maintenance_date, issue_description, maintenance_type, cost, status)
               VALUES (%s,%s,%s,%s,%s,%s,%s)''',
            (charger_id, staff_id, maintenance_date, issue_description, maintenance_type, cost, status)
        )
        flash('Maintenance record added.', 'success')
        return redirect(url_for('maintenance.list_maintenance'))

    return render_template('maintenance_form.html', record=None, chargers=chargers, staff=staff)


@maintenance_bp.route('/<int:maintenance_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_maintenance(maintenance_id):
    record   = execute_query('SELECT * FROM maintenance WHERE maintenance_id = %s', (maintenance_id,), fetchone=True)
    chargers = execute_query(
        'SELECT c.charger_id, c.charger_type, cs.station_name FROM charger c JOIN charging_station cs ON c.station_id=cs.station_id ORDER BY cs.station_name',
        fetch=True
    )
    staff = execute_query('SELECT staff_id, full_name, role FROM staff ORDER BY full_name', fetch=True)

    if not record:
        flash('Record not found.', 'danger')
        return redirect(url_for('maintenance.list_maintenance'))

    if request.method == 'POST':
        charger_id        = request.form.get('charger_id')
        staff_id          = request.form.get('staff_id')
        maintenance_date  = request.form.get('maintenance_date')
        issue_description = request.form.get('issue_description', '').strip()
        maintenance_type  = request.form.get('maintenance_type', '').strip()
        cost              = request.form.get('cost') or None
        status            = request.form.get('status', 'Scheduled')

        execute_query(
            '''UPDATE maintenance SET charger_id=%s, staff_id=%s, maintenance_date=%s,
               issue_description=%s, maintenance_type=%s, cost=%s, status=%s
               WHERE maintenance_id=%s''',
            (charger_id, staff_id, maintenance_date, issue_description, maintenance_type, cost, status, maintenance_id)
        )
        flash('Maintenance record updated.', 'success')
        return redirect(url_for('maintenance.list_maintenance'))

    return render_template('maintenance_form.html', record=record, chargers=chargers, staff=staff)


@maintenance_bp.route('/<int:maintenance_id>/delete', methods=['POST'])
@login_required
def delete_maintenance(maintenance_id):
    try:
        execute_query('DELETE FROM maintenance WHERE maintenance_id = %s', (maintenance_id,))
        flash('Record deleted.', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('maintenance.list_maintenance'))
