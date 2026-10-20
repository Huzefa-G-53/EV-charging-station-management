from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from routes.auth_routes import admin_required
from database.db_connection import execute_query
import mysql.connector

users_bp = Blueprint('users', __name__, url_prefix='/users')


@users_bp.route('/')
@admin_required
def list_users():
    search = request.args.get('search', '').strip()
    if search:
        users = execute_query(
            '''SELECT u.user_id, u.full_name, u.phone, u.email, u.account_status, u.suspension_reason, u.created_at,
                      (SELECT COUNT(*) FROM charging_session cs WHERE cs.user_id = u.user_id) AS session_count
               FROM user u
               WHERE u.full_name LIKE %s OR u.email LIKE %s OR u.phone LIKE %s
               ORDER BY u.user_id''',
            (f'%{search}%', f'%{search}%', f'%{search}%'), fetch=True
        )
    else:
        users = execute_query(
            '''SELECT u.user_id, u.full_name, u.phone, u.email, u.account_status, u.suspension_reason, u.created_at,
                      (SELECT COUNT(*) FROM charging_session cs WHERE cs.user_id = u.user_id) AS session_count
               FROM user u
               ORDER BY u.user_id''',
            fetch=True
        )
    return render_template('users_list.html', users=users, search=search)


@users_bp.route('/add', methods=['GET', 'POST'])
@admin_required
def add_user():
    """Admin can register an on-site walk-in customer."""
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        phone     = request.form.get('phone', '').strip()
        email     = request.form.get('email', '').strip()
        password  = request.form.get('password', '')
        address   = request.form.get('address', '').strip()

        if not all([full_name, phone, email, password]):
            flash('Full name, phone, email, and initial password are required.', 'danger')
            return render_template('users_form.html', user=None)

        password_hash = generate_password_hash(password)
        try:
            execute_query(
                '''INSERT INTO user (full_name, phone, email, password_hash, address, account_status)
                   VALUES (%s, %s, %s, %s, %s, 'Active')''',
                (full_name, phone, email, password_hash, address)
            )
            flash('Customer registered successfully.', 'success')
            return redirect(url_for('users.list_users'))
        except mysql.connector.IntegrityError:
            flash('Email already registered for another customer.', 'danger')
        except Exception:
            flash('Error creating customer record.', 'danger')

    return render_template('users_form.html', user=None)


@users_bp.route('/<int:user_id>/view')
@admin_required
def view_user(user_id):
    """
    Read-only operational profile view for Admin.
    Admin CANNOT edit customer personal details or passwords, and CANNOT delete customers.
    Admin sees only user name and contact info — no vehicles shown.
    """
    user = execute_query(
        '''SELECT user_id, full_name, phone, email, account_status, suspension_reason, created_at, address
           FROM user WHERE user_id = %s''',
        (user_id,), fetchone=True
    )
    if not user:
        flash('Customer not found.', 'danger')
        return redirect(url_for('users.list_users'))

    recent_sessions = execute_query(
        '''SELECT cs.*, c.charger_type, st.station_name
           FROM charging_session cs
           JOIN charger c ON cs.charger_id = c.charger_id
           JOIN charging_station st ON c.station_id = st.station_id
           WHERE cs.user_id = %s
           ORDER BY cs.session_id DESC LIMIT 5''',
        (user_id,), fetch=True
    )

    return render_template(
        'users_view.html',
        user=user,
        recent_sessions=recent_sessions
    )


@users_bp.route('/<int:user_id>/toggle-status', methods=['POST'])
@admin_required
def toggle_status(user_id):
    """Admin moderation: Suspend (requires mandatory reason) or activate an account."""
    user = execute_query('SELECT user_id, full_name, account_status FROM user WHERE user_id = %s', (user_id,), fetchone=True)
    if not user:
        flash('Customer not found.', 'danger')
        return redirect(url_for('users.list_users'))

    if user['account_status'] == 'Active':
        reason = request.form.get('suspension_reason', '').strip()
        if not reason:
            flash('A mandatory reason is required to suspend a customer account.', 'danger')
            return redirect(url_for('users.list_users'))

        execute_query(
            'UPDATE user SET account_status = %s, suspension_reason = %s WHERE user_id = %s',
            ('Suspended', reason, user_id)
        )
        flash(f"Account for {user['full_name']} has been suspended. Reason: {reason}", 'warning')
    else:
        execute_query(
            'UPDATE user SET account_status = %s, suspension_reason = NULL WHERE user_id = %s',
            ('Active', user_id)
        )
        flash(f"Account for {user['full_name']} has been reactivated.", 'success')

    return redirect(url_for('users.list_users'))
