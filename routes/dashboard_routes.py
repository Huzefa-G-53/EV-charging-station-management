import json
from flask import Blueprint, render_template
from routes.auth_routes import login_required
from database.db_connection import execute_query

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def index():
    # ── Counts ────────────────────────────────────────────────────────────────
    total_users    = execute_query('SELECT COUNT(*) AS c FROM user',             fetchone=True)['c']
    total_vehicles = execute_query('SELECT COUNT(*) AS c FROM vehicle',          fetchone=True)['c']
    total_stations = execute_query('SELECT COUNT(*) AS c FROM charging_station', fetchone=True)['c']
    total_chargers = execute_query('SELECT COUNT(*) AS c FROM charger',          fetchone=True)['c']
    active_sessions = execute_query(
        "SELECT COUNT(*) AS c FROM charging_session WHERE status = 'Active'",
        fetchone=True
    )['c']

    # ── Financials ────────────────────────────────────────────────────
    total_revenue  = execute_query('SELECT COALESCE(SUM(amount),0) AS t FROM revenue',  fetchone=True)['t'] or 0
    total_expenses = execute_query('SELECT COALESCE(SUM(amount),0) AS t FROM expenses', fetchone=True)['t'] or 0
    net_profit     = total_revenue - total_expenses

    # ── Chart data queries ────────────────────────────────────────────────────
    from datetime import datetime, timedelta

    # 1. Station Charger Real-Time Status & Charger IDs (For Bar Chart with Hover Details)
    station_status_rows = execute_query(
        '''SELECT cs.station_name,
                  SUM(CASE WHEN c.status = 'Available' THEN 1 ELSE 0 END) AS available,
                  SUM(CASE WHEN c.status = 'In Use' THEN 1 ELSE 0 END) AS in_use,
                  SUM(CASE WHEN c.status IN ('Under Maintenance', 'Inactive') THEN 1 ELSE 0 END) AS maintenance,
                  COUNT(c.charger_id) AS total_chargers,
                  COALESCE(GROUP_CONCAT(CASE WHEN c.status = 'Available' THEN CONCAT('#', c.charger_id) ELSE NULL END ORDER BY c.charger_id SEPARATOR ', '), 'None') AS avail_ids,
                  COALESCE(GROUP_CONCAT(CASE WHEN c.status = 'In Use' THEN CONCAT('#', c.charger_id) ELSE NULL END ORDER BY c.charger_id SEPARATOR ', '), 'None') AS in_use_ids
           FROM charging_station cs
           LEFT JOIN charger c ON cs.station_id = c.station_id
           GROUP BY cs.station_id, cs.station_name
           ORDER BY cs.station_name''',
        fetch=True
    )

    # 2. Daily Sessions Timeline Trend (7-Day Network Demand)
    today = datetime.now().date()
    date_range = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
    timeline_rows = execute_query(
        '''SELECT DATE(start_time) AS session_date,
                  COUNT(*) AS session_count,
                  COALESCE(SUM(energy_consumed), 0) AS total_kwh
           FROM charging_session
           WHERE start_time >= DATE_SUB(CURDATE(), INTERVAL 6 DAY)
           GROUP BY DATE(start_time)''',
        fetch=True
    )
    date_map = {r['session_date']: r for r in timeline_rows}
    timeline_labels = [d.strftime('%d %b') for d in date_range]
    timeline_sessions = [date_map[d]['session_count'] if d in date_map else 0 for d in date_range]
    timeline_kwh = [round(float(date_map[d]['total_kwh']), 1) if d in date_map else 0.0 for d in date_range]

    # 3. Station Energy Dispensed (Physical Output in kWh)
    station_energy_rows = execute_query(
        '''SELECT cs.station_name,
                  COALESCE(SUM(s.energy_consumed), 0) AS total_kwh,
                  COUNT(s.session_id) AS session_count
           FROM charging_station cs
           LEFT JOIN charger c ON cs.station_id = c.station_id
           LEFT JOIN charging_session s ON c.charger_id = s.charger_id
           GROUP BY cs.station_id, cs.station_name
           ORDER BY cs.station_name''',
        fetch=True
    )

    # Prepare JSON serializable payload for charts
    chart_payload = {
        'station_chargers': {
            'labels': [s['station_name'] for s in station_status_rows],
            'available': [int(s['available'] or 0) for s in station_status_rows],
            'in_use': [int(s['in_use'] or 0) for s in station_status_rows],
            'maintenance': [int(s['maintenance'] or 0) for s in station_status_rows],
            'avail_ids': [s['avail_ids'] for s in station_status_rows],
            'in_use_ids': [s['in_use_ids'] for s in station_status_rows],
            'totals': [int(s['total_chargers'] or 0) for s in station_status_rows]
        },
        'sessions_timeline': {
            'labels': timeline_labels,
            'sessions': timeline_sessions
        },
        'station_energy': {
            'labels': [s['station_name'] for s in station_energy_rows],
            'kwh': [round(float(s['total_kwh'] or 0), 1) for s in station_energy_rows],
            'sessions': [int(s['session_count'] or 0) for s in station_energy_rows]
        }
    }

    return render_template(
        'dashboard.html',
        total_users=total_users,
        total_vehicles=total_vehicles,
        total_stations=total_stations,
        total_chargers=total_chargers,
        active_sessions=active_sessions,
        total_revenue=total_revenue,
        total_expenses=total_expenses,
        net_profit=net_profit,
        chart_payload_json=json.dumps(chart_payload),
    )
