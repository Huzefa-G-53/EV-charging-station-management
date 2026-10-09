from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth_routes import login_required
from database.db_connection import execute_query
import mysql.connector

collaborations_bp = Blueprint('collaborations', __name__, url_prefix='/collaborations')

COLLAB_TYPES   = ['Advertisement Board', 'Land Rental', 'Cafe', 'Convenience Store', 'Other']
COLLAB_STATUSES = ['Active', 'Expired', 'Terminated', 'Pending']


@collaborations_bp.route('/')
@login_required
def list_collaborations():
    status_filter  = request.args.get('status', '')
    station_filter = request.args.get('station_id', '')
    stations = execute_query('SELECT station_id, station_name FROM charging_station ORDER BY station_name', fetch=True)

    query  = '''SELECT col.*, cs.station_name FROM collaborations col
                JOIN charging_station cs ON col.station_id = cs.station_id
                WHERE 1=1 '''
    params = []
    if status_filter:
        query += 'AND col.status = %s '
        params.append(status_filter)
    if station_filter:
        query += 'AND col.station_id = %s '
        params.append(station_filter)
    query += 'ORDER BY col.start_date DESC'

    collabs = execute_query(query, tuple(params), fetch=True)
    return render_template('collaborations_list.html', collabs=collabs, stations=stations,
                           collab_types=COLLAB_TYPES, collab_statuses=COLLAB_STATUSES,
                           status_filter=status_filter, station_filter=station_filter)


@collaborations_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_collaboration():
    stations = execute_query('SELECT station_id, station_name FROM charging_station ORDER BY station_name', fetch=True)

    if request.method == 'POST':
        station_id         = request.form.get('station_id')
        partner_name       = request.form.get('partner_name', '').strip()
        collaboration_type = request.form.get('collaboration_type')
        contact_person     = request.form.get('contact_person', '').strip()
        contact_number     = request.form.get('contact_number', '').strip()
        start_date         = request.form.get('start_date')
        end_date           = request.form.get('end_date') or None
        agreed_amount      = request.form.get('agreed_amount') or None
        status             = request.form.get('status', 'Active')
        description        = request.form.get('description', '').strip()

        if not all([station_id, partner_name, collaboration_type, start_date]):
            flash('Station, partner name, type, and start date are required.', 'danger')
            return render_template('collaborations_form.html', collab=None, stations=stations,
                                   collab_types=COLLAB_TYPES, collab_statuses=COLLAB_STATUSES)

        execute_query(
            '''INSERT INTO collaborations
               (station_id, partner_name, collaboration_type, contact_person, contact_number,
                start_date, end_date, agreed_amount, status, description)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
            (station_id, partner_name, collaboration_type, contact_person, contact_number,
             start_date, end_date, agreed_amount, status, description)
        )
        flash('Collaboration added.', 'success')
        return redirect(url_for('collaborations.list_collaborations'))

    return render_template('collaborations_form.html', collab=None, stations=stations,
                           collab_types=COLLAB_TYPES, collab_statuses=COLLAB_STATUSES)


@collaborations_bp.route('/<int:collaboration_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_collaboration(collaboration_id):
    collab   = execute_query('SELECT * FROM collaborations WHERE collaboration_id = %s', (collaboration_id,), fetchone=True)
    stations = execute_query('SELECT station_id, station_name FROM charging_station ORDER BY station_name', fetch=True)

    if not collab:
        flash('Collaboration not found.', 'danger')
        return redirect(url_for('collaborations.list_collaborations'))

    if request.method == 'POST':
        station_id         = request.form.get('station_id')
        partner_name       = request.form.get('partner_name', '').strip()
        collaboration_type = request.form.get('collaboration_type')
        contact_person     = request.form.get('contact_person', '').strip()
        contact_number     = request.form.get('contact_number', '').strip()
        start_date         = request.form.get('start_date')
        end_date           = request.form.get('end_date') or None
        agreed_amount      = request.form.get('agreed_amount') or None
        status             = request.form.get('status', 'Active')
        description        = request.form.get('description', '').strip()

        execute_query(
            '''UPDATE collaborations SET station_id=%s, partner_name=%s, collaboration_type=%s,
               contact_person=%s, contact_number=%s, start_date=%s, end_date=%s,
               agreed_amount=%s, status=%s, description=%s
               WHERE collaboration_id=%s''',
            (station_id, partner_name, collaboration_type, contact_person, contact_number,
             start_date, end_date, agreed_amount, status, description, collaboration_id)
        )
        flash('Collaboration updated.', 'success')
        return redirect(url_for('collaborations.list_collaborations'))

    return render_template('collaborations_form.html', collab=collab, stations=stations,
                           collab_types=COLLAB_TYPES, collab_statuses=COLLAB_STATUSES)


@collaborations_bp.route('/<int:collaboration_id>/delete', methods=['POST'])
@login_required
def delete_collaboration(collaboration_id):
    execute_query('DELETE FROM collaborations WHERE collaboration_id = %s', (collaboration_id,))
    flash('Collaboration deleted.', 'success')
    return redirect(url_for('collaborations.list_collaborations'))
