from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth_routes import login_required
from database.db_connection import execute_query
import mysql.connector

vehicles_bp = Blueprint('vehicles', __name__, url_prefix='/vehicles')


@vehicles_bp.route('/')
@login_required
def list_vehicles():
    search = request.args.get('search', '').strip()
    if search:
        vehicles = execute_query(
            '''SELECT v.*, u.full_name AS owner_name
               FROM vehicle v JOIN user u ON v.user_id = u.user_id
               WHERE v.vehicle_number LIKE %s OR v.brand LIKE %s OR u.full_name LIKE %s
               ORDER BY v.vehicle_id''',
            (f'%{search}%', f'%{search}%', f'%{search}%'), fetch=True
        )
    else:
        vehicles = execute_query(
            '''SELECT v.*, u.full_name AS owner_name
               FROM vehicle v JOIN user u ON v.user_id = u.user_id
               ORDER BY v.vehicle_id''',
            fetch=True
        )
    return render_template('vehicles_list.html', vehicles=vehicles, search=search)


@vehicles_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_vehicle():
    users = execute_query("SELECT user_id, full_name FROM user WHERE account_status='Active' ORDER BY full_name", fetch=True)

    if request.method == 'POST':
        user_id          = request.form.get('user_id')
        vehicle_number   = request.form.get('vehicle_number', '').strip().upper()
        vehicle_type     = request.form.get('vehicle_type', '').strip()
        brand            = request.form.get('brand', '').strip()
        model            = request.form.get('model', '').strip()
        battery_capacity = request.form.get('battery_capacity', '')

        if not all([user_id, vehicle_number, vehicle_type, brand, model, battery_capacity]):
            flash('All fields are required.', 'danger')
            return render_template('vehicles_form.html', vehicle=None, users=users)

        try:
            execute_query(
                '''INSERT INTO vehicle (user_id, vehicle_number, vehicle_type, brand, model, battery_capacity)
                   VALUES (%s, %s, %s, %s, %s, %s)''',
                (user_id, vehicle_number, vehicle_type, brand, model, battery_capacity)
            )
            flash('Vehicle added successfully.', 'success')
            return redirect(url_for('vehicles.list_vehicles'))
        except mysql.connector.IntegrityError:
            flash('Vehicle number already exists.', 'danger')

    return render_template('vehicles_form.html', vehicle=None, users=users)


@vehicles_bp.route('/<int:vehicle_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_vehicle(vehicle_id):
    vehicle = execute_query('SELECT * FROM vehicle WHERE vehicle_id = %s', (vehicle_id,), fetchone=True)
    if not vehicle:
        flash('Vehicle not found.', 'danger')
        return redirect(url_for('vehicles.list_vehicles'))

    users = execute_query("SELECT user_id, full_name FROM user ORDER BY full_name", fetch=True)

    if request.method == 'POST':
        user_id          = request.form.get('user_id')
        vehicle_number   = request.form.get('vehicle_number', '').strip().upper()
        vehicle_type     = request.form.get('vehicle_type', '').strip()
        brand            = request.form.get('brand', '').strip()
        model            = request.form.get('model', '').strip()
        battery_capacity = request.form.get('battery_capacity', '')

        try:
            execute_query(
                '''UPDATE vehicle SET user_id=%s, vehicle_number=%s, vehicle_type=%s,
                   brand=%s, model=%s, battery_capacity=%s WHERE vehicle_id=%s''',
                (user_id, vehicle_number, vehicle_type, brand, model, battery_capacity, vehicle_id)
            )
            flash('Vehicle updated successfully.', 'success')
            return redirect(url_for('vehicles.list_vehicles'))
        except mysql.connector.IntegrityError:
            flash('Vehicle number already exists.', 'danger')

    return render_template('vehicles_form.html', vehicle=vehicle, users=users)


@vehicles_bp.route('/<int:vehicle_id>/delete', methods=['POST'])
@login_required
def delete_vehicle(vehicle_id):
    try:
        execute_query('DELETE FROM vehicle WHERE vehicle_id = %s', (vehicle_id,))
        flash('Vehicle deleted successfully.', 'success')
    except mysql.connector.IntegrityError:
        flash('Cannot delete: this vehicle has associated charging sessions.', 'danger')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('vehicles.list_vehicles'))
