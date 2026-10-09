from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from routes.auth_routes import login_required
from database.db_connection import execute_query
import mysql.connector

users_bp = Blueprint('users', __name__, url_prefix='/users')


@users_bp.route('/')
@login_required
def list_users():
    search = request.args.get('search', '').strip()
    if search:
        users = execute_query(
            'SELECT * FROM user WHERE full_name LIKE %s OR email LIKE %s OR phone LIKE %s ORDER BY user_id',
            (f'%{search}%', f'%{search}%', f'%{search}%'), fetch=True
        )
    else:
        users = execute_query('SELECT * FROM user ORDER BY user_id', fetch=True)
    return render_template('users_list.html', users=users, search=search)


@users_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if request.method == 'POST':
        full_name  = request.form.get('full_name', '').strip()
        phone      = request.form.get('phone', '').strip()
        email      = request.form.get('email', '').strip()
        password   = request.form.get('password', '')
        address    = request.form.get('address', '').strip()
        status     = request.form.get('account_status', 'Active')

        if not all([full_name, phone, email, password]):
            flash('Full name, phone, email, and password are required.', 'danger')
            return render_template('users_form.html', user=None)

        password_hash = generate_password_hash(password)
        try:
            execute_query(
                '''INSERT INTO user (full_name, phone, email, password_hash, address, account_status)
                   VALUES (%s, %s, %s, %s, %s, %s)''',
                (full_name, phone, email, password_hash, address, status)
            )
            flash('User added successfully.', 'success')
            return redirect(url_for('users.list_users'))
        except mysql.connector.IntegrityError:
            flash('Email already exists. Please use a different email.', 'danger')

    return render_template('users_form.html', user=None)


@users_bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = execute_query('SELECT * FROM user WHERE user_id = %s', (user_id,), fetchone=True)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('users.list_users'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        phone     = request.form.get('phone', '').strip()
        email     = request.form.get('email', '').strip()
        address   = request.form.get('address', '').strip()
        status    = request.form.get('account_status', 'Active')
        password  = request.form.get('password', '').strip()

        if not all([full_name, phone, email]):
            flash('Full name, phone, and email are required.', 'danger')
            return render_template('users_form.html', user=user)

        if password:
            password_hash = generate_password_hash(password)
            try:
                execute_query(
                    '''UPDATE user SET full_name=%s, phone=%s, email=%s, password_hash=%s,
                       address=%s, account_status=%s WHERE user_id=%s''',
                    (full_name, phone, email, password_hash, address, status, user_id)
                )
            except mysql.connector.IntegrityError:
                flash('Email already exists.', 'danger')
                return render_template('users_form.html', user=user)
        else:
            try:
                execute_query(
                    '''UPDATE user SET full_name=%s, phone=%s, email=%s,
                       address=%s, account_status=%s WHERE user_id=%s''',
                    (full_name, phone, email, address, status, user_id)
                )
            except mysql.connector.IntegrityError:
                flash('Email already exists.', 'danger')
                return render_template('users_form.html', user=user)

        flash('User updated successfully.', 'success')
        return redirect(url_for('users.list_users'))

    return render_template('users_form.html', user=user)


@users_bp.route('/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    try:
        execute_query('DELETE FROM user WHERE user_id = %s', (user_id,))
        flash('User deleted successfully.', 'success')
    except mysql.connector.IntegrityError:
        flash('Cannot delete: this user has associated vehicles or sessions. Remove them first.', 'danger')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('users.list_users'))
