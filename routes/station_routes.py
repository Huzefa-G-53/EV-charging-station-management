from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth_routes import login_required
from database.db_connection import execute_query
import mysql.connector

stations_bp = Blueprint('stations', __name__, url_prefix='/stations')


@stations_bp.route('/')
@login_required
def list_stations():
    search = request.args.get('search', '').strip()
    if search:
        stations = execute_query(
            'SELECT * FROM charging_station WHERE station_name LIKE %s OR address LIKE %s ORDER BY station_id',
            (f'%{search}%', f'%{search}%'), fetch=True
        )
    else:
        stations = execute_query('SELECT * FROM charging_station ORDER BY station_id', fetch=True)
    return render_template('stations_list.html', stations=stations, search=search)


@stations_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_station():
    if request.method == 'POST':
        station_name   = request.form.get('station_name', '').strip()
        address        = request.form.get('address', '').strip()
        contact_number = request.form.get('contact_number', '').strip()
        num_chargers   = request.form.get('number_of_chargers', 0) or 0
        op_hours       = request.form.get('operating_hours', '').strip()
        status         = request.form.get('status', 'Active')

        if not all([station_name, address]):
            flash('Station name and address are required.', 'danger')
            return render_template('stations_form.html', station=None)

        execute_query(
            '''INSERT INTO charging_station (station_name, address, contact_number, number_of_chargers, operating_hours, status)
               VALUES (%s, %s, %s, %s, %s, %s)''',
            (station_name, address, contact_number, num_chargers, op_hours, status)
        )
        flash('Charging station added successfully.', 'success')
        return redirect(url_for('stations.list_stations'))

    return render_template('stations_form.html', station=None)


@stations_bp.route('/<int:station_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_station(station_id):
    station = execute_query('SELECT * FROM charging_station WHERE station_id = %s', (station_id,), fetchone=True)
    if not station:
        flash('Station not found.', 'danger')
        return redirect(url_for('stations.list_stations'))

    if request.method == 'POST':
        station_name   = request.form.get('station_name', '').strip()
        address        = request.form.get('address', '').strip()
        contact_number = request.form.get('contact_number', '').strip()
        num_chargers   = request.form.get('number_of_chargers', 0) or 0
        op_hours       = request.form.get('operating_hours', '').strip()
        status         = request.form.get('status', 'Active')

        execute_query(
            '''UPDATE charging_station SET station_name=%s, address=%s, contact_number=%s,
               number_of_chargers=%s, operating_hours=%s, status=%s WHERE station_id=%s''',
            (station_name, address, contact_number, num_chargers, op_hours, status, station_id)
        )
        flash('Station updated successfully.', 'success')
        return redirect(url_for('stations.list_stations'))

    return render_template('stations_form.html', station=station)


@stations_bp.route('/<int:station_id>/delete', methods=['POST'])
@login_required
def delete_station(station_id):
    try:
        execute_query('DELETE FROM charging_station WHERE station_id = %s', (station_id,))
        flash('Station deleted successfully.', 'success')
    except mysql.connector.IntegrityError:
        flash('Cannot delete: this station has associated chargers, staff, or financial records.', 'danger')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('stations.list_stations'))
