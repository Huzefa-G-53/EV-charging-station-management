from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth_routes import login_required
from database.db_connection import execute_query

expenses_bp = Blueprint('expenses', __name__, url_prefix='/expenses')

EXPENSE_TYPES = ['Salary', 'Charger Maintenance', 'Station Maintenance',
                 'Electricity', 'Rent', 'Equipment', 'Utilities', 'Other']


@expenses_bp.route('/')
@login_required
def list_expenses():
    type_filter    = request.args.get('expense_type', '')
    station_filter = request.args.get('station_id', '')
    stations = execute_query('SELECT station_id, station_name FROM charging_station ORDER BY station_name', fetch=True)

    query  = '''SELECT e.*, cs.station_name FROM expenses e
                JOIN charging_station cs ON e.station_id = cs.station_id
                WHERE 1=1 '''
    params = []
    if type_filter:
        query += 'AND e.expense_type = %s '
        params.append(type_filter)
    if station_filter:
        query += 'AND e.station_id = %s '
        params.append(station_filter)
    query += 'ORDER BY e.expense_date DESC'

    expenses = execute_query(query, tuple(params), fetch=True)
    total = sum(float(e['amount']) for e in expenses)
    return render_template('expenses_list.html', expenses=expenses, stations=stations,
                           expense_types=EXPENSE_TYPES, type_filter=type_filter,
                           station_filter=station_filter, total=total)


@expenses_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_expense():
    stations = execute_query('SELECT station_id, station_name FROM charging_station ORDER BY station_name', fetch=True)

    if request.method == 'POST':
        station_id   = request.form.get('station_id')
        expense_date = request.form.get('expense_date')
        amount       = request.form.get('amount', '')
        expense_type = request.form.get('expense_type')
        description  = request.form.get('description', '').strip()

        if not all([station_id, expense_date, amount, expense_type]):
            flash('Station, date, amount, and type are required.', 'danger')
            return render_template('expenses_form.html', expense=None, stations=stations, expense_types=EXPENSE_TYPES)

        execute_query(
            'INSERT INTO expenses (station_id, expense_date, amount, expense_type, description) VALUES (%s,%s,%s,%s,%s)',
            (station_id, expense_date, amount, expense_type, description)
        )
        flash('Expense recorded.', 'success')
        return redirect(url_for('expenses.list_expenses'))

    return render_template('expenses_form.html', expense=None, stations=stations, expense_types=EXPENSE_TYPES)


@expenses_bp.route('/<int:expense_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_expense(expense_id):
    expense  = execute_query('SELECT * FROM expenses WHERE expense_id = %s', (expense_id,), fetchone=True)
    stations = execute_query('SELECT station_id, station_name FROM charging_station ORDER BY station_name', fetch=True)

    if not expense:
        flash('Expense not found.', 'danger')
        return redirect(url_for('expenses.list_expenses'))

    if request.method == 'POST':
        station_id   = request.form.get('station_id')
        expense_date = request.form.get('expense_date')
        amount       = request.form.get('amount', '')
        expense_type = request.form.get('expense_type')
        description  = request.form.get('description', '').strip()

        execute_query(
            'UPDATE expenses SET station_id=%s, expense_date=%s, amount=%s, expense_type=%s, description=%s WHERE expense_id=%s',
            (station_id, expense_date, amount, expense_type, description, expense_id)
        )
        flash('Expense updated.', 'success')
        return redirect(url_for('expenses.list_expenses'))

    return render_template('expenses_form.html', expense=expense, stations=stations, expense_types=EXPENSE_TYPES)


@expenses_bp.route('/<int:expense_id>/delete', methods=['POST'])
@login_required
def delete_expense(expense_id):
    execute_query('DELETE FROM expenses WHERE expense_id = %s', (expense_id,))
    flash('Expense deleted.', 'success')
    return redirect(url_for('expenses.list_expenses'))
