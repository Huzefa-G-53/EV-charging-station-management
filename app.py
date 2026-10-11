from flask import Flask
from config import Config

from routes.auth_routes         import auth_bp
from routes.dashboard_routes    import dashboard_bp
from routes.user_routes         import users_bp
from routes.vehicle_routes      import vehicles_bp
from routes.station_routes      import stations_bp
from routes.charger_routes      import chargers_bp
from routes.session_routes      import sessions_bp
from routes.payment_routes      import payments_bp
from routes.staff_routes        import staff_bp
from routes.maintenance_routes  import maintenance_bp
from routes.expense_routes      import expenses_bp
from routes.revenue_routes      import revenue_bp
from routes.collaboration_routes import collaborations_bp
from routes.report_routes       import reports_bp
from routes.customer_routes     import customer_bp


def create_app():
    app = Flask(__name__)
    app.secret_key = Config.SECRET_KEY

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(vehicles_bp)
    app.register_blueprint(stations_bp)
    app.register_blueprint(chargers_bp)
    app.register_blueprint(sessions_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(maintenance_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(revenue_bp)
    app.register_blueprint(collaborations_bp)
    app.register_blueprint(reports_bp)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=Config.DEBUG)
