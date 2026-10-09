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

    # ── Financials ────────────────────────────────────────────────────────────
    total_revenue  = execute_query('SELECT COALESCE(SUM(amount),0) AS t FROM revenue',  fetchone=True)['t'] or 0
    total_expenses = execute_query('SELECT COALESCE(SUM(amount),0) AS t FROM expenses', fetchone=True)['t'] or 0
    net_profit     = total_revenue - total_expenses

    # ── Chart data ────────────────────────────────────────────────────────────
    revenue_by_source  = execute_query(
        'SELECT source, SUM(amount) AS total FROM revenue GROUP BY source ORDER BY total DESC',
        fetch=True
    )
    expenses_by_type   = execute_query(
        'SELECT expense_type, SUM(amount) AS total FROM expenses GROUP BY expense_type ORDER BY total DESC',
        fetch=True
    )
    charger_status     = execute_query(
        'SELECT status, COUNT(*) AS cnt FROM charger GROUP BY status',
        fetch=True
    )
    session_status     = execute_query(
        'SELECT status, COUNT(*) AS cnt FROM charging_session GROUP BY status',
        fetch=True
    )

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
        revenue_by_source=revenue_by_source,
        expenses_by_type=expenses_by_type,
        charger_status=charger_status,
        session_status=session_status,
    )
