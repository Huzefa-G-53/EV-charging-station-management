from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth_routes import login_required
from database.db_connection import execute_query

revenue_bp = Blueprint('revenue', __name__, url_prefix='/revenue')

REVENUE_SOURCES = ['Charging Session', 'Advertisement', 'Land Rent',
                   'Cafe Rent', 'Convenience Store Rent', 'Other']


@revenue_bp.route('/')
@login_required
def list_revenue():
    source_filter  = request.args.get('source', '')
    station_filter = request.args.get('station_id', '')
    stations = execute_query('SELECT station_id, station_name FROM charging_station ORDER BY station_name', fetch=True)

    query  = '''SELECT r.*, cs.station_name FROM revenue r
                JOIN charging_station cs ON r.station_id = cs.station_id
                WHERE 1=1 '''
    params = []
    if source_filter:
        query += 'AND r.source = %s '
        params.append(source_filter)
    if station_filter:
        query += 'AND r.station_id = %s '
        params.append(station_filter)
    query += 'ORDER BY r.revenue_date DESC'

    revenues = execute_query(query, tuple(params), fetch=True)
    total = sum(float(r['amount']) for r in revenues)
    return render_template('revenue_list.html', revenues=revenues, stations=stations,
                           revenue_sources=REVENUE_SOURCES, source_filter=source_filter,
                           station_filter=station_filter, total=total)


@revenue_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_revenue():
    stations = execute_query('SELECT station_id, station_name FROM charging_station ORDER BY station_name', fetch=True)

    if request.method == 'POST':
        station_id   = request.form.get('station_id')
        revenue_date = request.form.get('revenue_date')
        amount       = request.form.get('amount', '')
        source       = request.form.get('source')
        description  = request.form.get('description', '').strip()

        if not all([station_id, revenue_date, amount, source]):
            flash('Station, date, amount, and source are required.', 'danger')
            return render_template('revenue_form.html', revenue=None, stations=stations, revenue_sources=REVENUE_SOURCES)

        execute_query(
            'INSERT INTO revenue (station_id, revenue_date, amount, source, description) VALUES (%s,%s,%s,%s,%s)',
            (station_id, revenue_date, amount, source, description)
        )
        flash('Revenue recorded.', 'success')
        return redirect(url_for('revenue.list_revenue'))

    return render_template('revenue_form.html', revenue=None, stations=stations, revenue_sources=REVENUE_SOURCES)


@revenue_bp.route('/<int:revenue_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_revenue(revenue_id):
    rev      = execute_query('SELECT * FROM revenue WHERE revenue_id = %s', (revenue_id,), fetchone=True)
    stations = execute_query('SELECT station_id, station_name FROM charging_station ORDER BY station_name', fetch=True)

    if not rev:
        flash('Revenue record not found.', 'danger')
        return redirect(url_for('revenue.list_revenue'))

    if request.method == 'POST':
        station_id   = request.form.get('station_id')
        revenue_date = request.form.get('revenue_date')
        amount       = request.form.get('amount', '')
        source       = request.form.get('source')
        description  = request.form.get('description', '').strip()

        execute_query(
            'UPDATE revenue SET station_id=%s, revenue_date=%s, amount=%s, source=%s, description=%s WHERE revenue_id=%s',
            (station_id, revenue_date, amount, source, description, revenue_id)
        )
        flash('Revenue updated.', 'success')
        return redirect(url_for('revenue.list_revenue'))

    return render_template('revenue_form.html', revenue=rev, stations=stations, revenue_sources=REVENUE_SOURCES)


@revenue_bp.route('/<int:revenue_id>/delete', methods=['POST'])
@login_required
def delete_revenue(revenue_id):
    execute_query('DELETE FROM revenue WHERE revenue_id = %s', (revenue_id,))
    flash('Revenue record deleted.', 'success')
    return redirect(url_for('revenue.list_revenue'))
