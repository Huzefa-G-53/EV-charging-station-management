from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth_routes import login_required
from database.db_connection import execute_query
import mysql.connector

payments_bp = Blueprint('payments', __name__, url_prefix='/payments')


@payments_bp.route('/')
@login_required
def list_payments():
    status_filter = request.args.get('status', '')
    if status_filter:
        payments = execute_query(
            '''SELECT p.*, u.full_name AS user_name, cs.session_id
               FROM payment p
               JOIN charging_session cs ON p.session_id = cs.session_id
               JOIN user u              ON cs.user_id   = u.user_id
               WHERE p.payment_status = %s
               ORDER BY p.payment_id DESC''',
            (status_filter,), fetch=True
        )
    else:
        payments = execute_query(
            '''SELECT p.*, u.full_name AS user_name
               FROM payment p
               JOIN charging_session cs ON p.session_id = cs.session_id
               JOIN user u              ON cs.user_id   = u.user_id
               ORDER BY p.payment_id DESC''',
            fetch=True
        )
    return render_template('payments_list.html', payments=payments, status_filter=status_filter)


@payments_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_payment():
    # Only sessions without a payment
    sessions = execute_query(
        '''SELECT cs.session_id, u.full_name, cs.total_amount
           FROM charging_session cs
           JOIN user u ON cs.user_id = u.user_id
           WHERE cs.session_id NOT IN (SELECT session_id FROM payment)
           AND cs.status = 'Completed'
           ORDER BY cs.session_id DESC''',
        fetch=True
    )

    if request.method == 'POST':
        session_id     = request.form.get('session_id')
        payment_date   = request.form.get('payment_date')
        amount         = request.form.get('amount', '')
        payment_method = request.form.get('payment_method')
        payment_status = request.form.get('payment_status', 'Completed')

        if not all([session_id, payment_date, amount, payment_method]):
            flash('All fields are required.', 'danger')
            return render_template('payments_form.html', payment=None, sessions=sessions)

        try:
            execute_query(
                'INSERT INTO payment (session_id, payment_date, amount, payment_method, payment_status) VALUES (%s,%s,%s,%s,%s)',
                (session_id, payment_date, amount, payment_method, payment_status)
            )
            flash('Payment recorded successfully.', 'success')
            return redirect(url_for('payments.list_payments'))
        except mysql.connector.IntegrityError:
            flash('A payment already exists for this session.', 'danger')

    return render_template('payments_form.html', payment=None, sessions=sessions)


@payments_bp.route('/<int:payment_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_payment(payment_id):
    payment = execute_query('SELECT * FROM payment WHERE payment_id = %s', (payment_id,), fetchone=True)
    if not payment:
        flash('Payment not found.', 'danger')
        return redirect(url_for('payments.list_payments'))

    sessions = execute_query(
        'SELECT cs.session_id, u.full_name, cs.total_amount FROM charging_session cs JOIN user u ON cs.user_id=u.user_id ORDER BY cs.session_id DESC',
        fetch=True
    )

    if request.method == 'POST':
        payment_date   = request.form.get('payment_date')
        amount         = request.form.get('amount', '')
        payment_method = request.form.get('payment_method')
        payment_status = request.form.get('payment_status', 'Completed')

        execute_query(
            'UPDATE payment SET payment_date=%s, amount=%s, payment_method=%s, payment_status=%s WHERE payment_id=%s',
            (payment_date, amount, payment_method, payment_status, payment_id)
        )
        flash('Payment updated successfully.', 'success')
        return redirect(url_for('payments.list_payments'))

    return render_template('payments_form.html', payment=payment, sessions=sessions)


@payments_bp.route('/<int:payment_id>/delete', methods=['POST'])
@login_required
def delete_payment(payment_id):
    try:
        execute_query('DELETE FROM payment WHERE payment_id = %s', (payment_id,))
        flash('Payment deleted successfully.', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('payments.list_payments'))
