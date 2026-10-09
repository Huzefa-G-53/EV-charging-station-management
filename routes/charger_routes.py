from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth_routes import login_required
from database.db_connection import execute_query
import mysql.connector

chargers_bp = Blueprint('chargers', __name__, url_prefix='/chargers')


@chargers_bp.route('/')
@login_required
def list_chargers():
    station_filter = request.args.get('station_id', '')
    stations = execute_query('SELECT station_id, station_name FROM charging_station ORDER BY station_name', fetch=True)

    if station_filter:
        chargers = execute_query(
            '''SELECT c.*, cs.station_name
               FROM charger c JOIN charging_station cs ON c.station_id = cs.station_id
               WHERE c.station_id = %s ORDER BY c.charger_id''',
            (station_filter,), fetch=True
        )
    else:
        chargers = execute_query(
            '''SELECT c.*, cs.station_name
               FROM charger c JOIN charging_station cs ON c.station_id = cs.station_id
               ORDER BY c.charger_id''',
            fetch=True
        )
    return render_template('chargers_list.html', chargers=chargers, stations=stations, station_filter=station_filter)


@chargers_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_charger():
    stations = execute_query("SELECT station_id, station_name FROM charging_station WHERE status='Active' ORDER BY station_name", fetch=True)

    if request.method == 'POST':
        station_id    = request.form.get('station_id')
        charger_type  = request.form.get('charger_type', '').strip()
        power_rating  = request.form.get('power_rating', '')
        price_per_kwh = request.form.get('price_per_kwh', '')
        status        = request.form.get('status', 'Available')

        if not all([station_id, charger_type, power_rating, price_per_kwh]):
            flash('All fields are required.', 'danger')
            return render_template('chargers_form.html', charger=None, stations=stations)

        execute_query(
            'INSERT INTO charger (station_id, charger_type, power_rating, price_per_kwh, status) VALUES (%s,%s,%s,%s,%s)',
            (station_id, charger_type, power_rating, price_per_kwh, status)
        )
        flash('Charger added successfully.', 'success')
        return redirect(url_for('chargers.list_chargers'))

    return render_template('chargers_form.html', charger=None, stations=stations)


@chargers_bp.route('/<int:charger_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_charger(charger_id):
    charger  = execute_query('SELECT * FROM charger WHERE charger_id = %s', (charger_id,), fetchone=True)
    stations = execute_query('SELECT station_id, station_name FROM charging_station ORDER BY station_name', fetch=True)

    if not charger:
        flash('Charger not found.', 'danger')
        return redirect(url_for('chargers.list_chargers'))

    if request.method == 'POST':
        station_id    = request.form.get('station_id')
        charger_type  = request.form.get('charger_type', '').strip()
        power_rating  = request.form.get('power_rating', '')
        price_per_kwh = request.form.get('price_per_kwh', '')
        status        = request.form.get('status', 'Available')

        execute_query(
            '''UPDATE charger SET station_id=%s, charger_type=%s, power_rating=%s,
               price_per_kwh=%s, status=%s WHERE charger_id=%s''',
            (station_id, charger_type, power_rating, price_per_kwh, status, charger_id)
        )
        flash('Charger updated successfully.', 'success')
        return redirect(url_for('chargers.list_chargers'))

    return render_template('chargers_form.html', charger=charger, stations=stations)


@chargers_bp.route('/<int:charger_id>/delete', methods=['POST'])
@login_required
def delete_charger(charger_id):
    try:
        execute_query('DELETE FROM charger WHERE charger_id = %s', (charger_id,))
        flash('Charger deleted successfully.', 'success')
    except mysql.connector.IntegrityError:
        flash('Cannot delete: this charger has associated sessions or maintenance records.', 'danger')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('chargers.list_chargers'))
