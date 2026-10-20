import json
from flask import Blueprint, render_template
from routes.auth_routes import login_required
from database.db_connection import execute_query

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')


@reports_bp.route('/')
@login_required
def index():
    # ── Financial summary ─────────────────────────────────────────────────────
    total_revenue  = execute_query('SELECT COALESCE(SUM(amount),0) AS t FROM revenue',  fetchone=True)['t'] or 0
    total_expenses = execute_query('SELECT COALESCE(SUM(amount),0) AS t FROM expenses', fetchone=True)['t'] or 0
    net_profit     = total_revenue - total_expenses

    # ── Revenue by source ─────────────────────────────────────────────────────
    revenue_by_source = execute_query(
        'SELECT source, SUM(amount) AS total FROM revenue GROUP BY source ORDER BY total DESC',
        fetch=True
    )

    # ── Expenses by type ──────────────────────────────────────────────────────
    expenses_by_type = execute_query(
        'SELECT expense_type, SUM(amount) AS total FROM expenses GROUP BY expense_type ORDER BY total DESC',
        fetch=True
    )

    # ── Station-wise revenue & expenses ───────────────────────────────────────
    station_revenue = execute_query(
        '''SELECT cs.station_name, COALESCE(SUM(r.amount),0) AS total
           FROM charging_station cs
           LEFT JOIN revenue r ON cs.station_id = r.station_id
           GROUP BY cs.station_id, cs.station_name
           ORDER BY cs.station_name''',
        fetch=True
    )
    station_expenses = execute_query(
        '''SELECT cs.station_name, COALESCE(SUM(e.amount),0) AS total
           FROM charging_station cs
           LEFT JOIN expenses e ON cs.station_id = e.station_id
           GROUP BY cs.station_id, cs.station_name
           ORDER BY cs.station_name''',
        fetch=True
    )

    # ── Charger & session stats ────────────────────────────────────────────────
    charger_status  = execute_query('SELECT status, COUNT(*) AS cnt FROM charger GROUP BY status', fetch=True)
    session_status  = execute_query('SELECT status, COUNT(*) AS cnt FROM charging_session GROUP BY status', fetch=True)
    active_chargers = execute_query(
        '''SELECT c.charger_id, c.charger_type, c.power_rating, cs.station_name
           FROM charger c JOIN charging_station cs ON c.station_id = cs.station_id
           WHERE c.status = 'Available' ORDER BY cs.station_name''',
        fetch=True
    )
    active_sessions = execute_query(
        '''SELECT cs.session_id, u.full_name, v.vehicle_number, cs.start_time, st.station_name
           FROM charging_session cs
           JOIN user u              ON cs.user_id    = u.user_id
           JOIN vehicle v           ON cs.vehicle_id = v.vehicle_id
           JOIN charger c           ON cs.charger_id = c.charger_id
           JOIN charging_station st ON c.station_id  = st.station_id
           WHERE cs.status = 'Active'
           ORDER BY cs.start_time''',
        fetch=True
    )

    # ── Maintenance summary ────────────────────────────────────────────────────
    maintenance_summary = execute_query(
        'SELECT status, COUNT(*) AS cnt, COALESCE(SUM(cost),0) AS total_cost FROM maintenance GROUP BY status',
        fetch=True
    )

    # Build P&L mappings for station comparison chart
    exp_map = {e['station_name']: float(e['total']) for e in station_expenses}
    rev_map = {r['station_name']: float(r['total']) for r in station_revenue}
    station_names = [r['station_name'] for r in station_revenue]

    # Clean display names for charts
    clean_names = [
        s.replace(' EV Station', '').replace(' Charging Hub', '').replace(' Charging Station', '')
        for s in station_names
    ]

    chart_payload = {
        'revenue': {
            'labels': [r['source'] for r in revenue_by_source],
            'values': [float(r['total']) for r in revenue_by_source]
        },
        'expenses': {
            'labels': [e['expense_type'] for e in expenses_by_type],
            'values': [float(e['total']) for e in expenses_by_type]
        },
        'station_pnl': {
            'labels': clean_names,
            'revenue': [rev_map.get(s, 0.0) for s in station_names],
            'expenses': [exp_map.get(s, 0.0) for s in station_names]
        },
        'financial_split': {
            'labels': ['Total Expenses', 'Net Profit Margin'],
            'values': [float(total_expenses), float(max(0, net_profit))]
        }
    }

    return render_template(
        'reports.html',
        total_revenue=total_revenue,
        total_expenses=total_expenses,
        net_profit=net_profit,
        revenue_by_source=revenue_by_source,
        expenses_by_type=expenses_by_type,
        station_revenue=station_revenue,
        station_expenses=station_expenses,
        charger_status=charger_status,
        session_status=session_status,
        active_chargers=active_chargers,
        active_sessions=active_sessions,
        maintenance_summary=maintenance_summary,
        chart_payload_json=json.dumps(chart_payload),
    )
