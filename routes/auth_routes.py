from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from database.db_connection import execute_query
import mysql.connector

auth_bp = Blueprint('auth', __name__)


# ── Auth Decorators ───────────────────────────────────────────────────────────
def admin_required(f):
    """Decorator to protect Admin-only endpoints."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_id' not in session or session.get('role') != 'admin':
            flash('Admin access required. Please log in with admin credentials.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def customer_required(f):
    """Decorator to protect Customer-only endpoints."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'customer':
            flash('Customer login required. Please log in to your account.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


# Legacy alias so existing admin routes continue to work smoothly
login_required = admin_required


# ── Core Routes ───────────────────────────────────────────────────────────────
@auth_bp.route('/')
def index():
    if session.get('role') == 'admin' and 'admin_id' in session:
        return redirect(url_for('dashboard.index'))
    elif session.get('role') == 'customer' and 'user_id' in session:
        return redirect(url_for('customer.dashboard'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('role') == 'admin' and 'admin_id' in session:
        return redirect(url_for('dashboard.index'))
    elif session.get('role') == 'customer' and 'user_id' in session:
        return redirect(url_for('customer.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please enter both email and password.', 'warning')
            return render_template('login.html')

        # 1. First, check if this is an Admin
        admin = execute_query(
            'SELECT * FROM admin WHERE email = %s',
            (email,), fetchone=True
        )
        if admin and check_password_hash(admin['password_hash'], password):
            session.clear()
            session['admin_id'] = admin['admin_id']
            session['admin_name'] = admin['full_name']
            session['role'] = 'admin'
            flash(f'Welcome back, {admin["full_name"]} (Administrator)', 'success')
            return redirect(url_for('dashboard.index'))

        # 2. If not admin, check if this is a Customer (User)
        user = execute_query(
            'SELECT * FROM user WHERE email = %s',
            (email,), fetchone=True
        )
        if user and check_password_hash(user['password_hash'], password):
            if user['account_status'] == 'Suspended':
                flash('Your account has been suspended. Please contact customer support.', 'danger')
                return render_template('login.html')

            session.clear()
            session['user_id'] = user['user_id']
            session['user_name'] = user['full_name']
            session['user_email'] = user['email']
            session['role'] = 'customer'
            flash(f'Welcome back, {user["full_name"]}!', 'success')
            return redirect(url_for('customer.dashboard'))

        flash('Invalid email or password.', 'danger')

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('role') == 'admin' and 'admin_id' in session:
        return redirect(url_for('dashboard.index'))
    elif session.get('role') == 'customer' and 'user_id' in session:
        return redirect(url_for('customer.dashboard'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not all([full_name, phone, email, password, confirm_password]):
            flash('All required fields must be filled in.', 'danger')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')

        # Check existing user
        existing = execute_query('SELECT user_id FROM user WHERE email = %s', (email,), fetchone=True)
        if existing:
            flash('An account with this email already exists. Please log in.', 'danger')
            return render_template('register.html')

        password_hash = generate_password_hash(password)
        try:
            user_id = execute_query(
                '''INSERT INTO user (full_name, phone, email, password_hash, address, account_status)
                   VALUES (%s, %s, %s, %s, %s, 'Active')''',
                (full_name, phone, email, password_hash, address)
            )
            session.clear()
            session['user_id'] = user_id
            session['user_name'] = full_name
            session['user_email'] = email
            session['role'] = 'customer'
            flash('Account created successfully! Welcome to GreenVolt.', 'success')
            return redirect(url_for('customer.dashboard'))
        except mysql.connector.IntegrityError:
            flash('Email already registered. Please log in or use a different email.', 'danger')
        except Exception:
            flash('An error occurred during registration. Please try again.', 'danger')

    return render_template('register.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
