from __future__ import annotations

import sys

from flask import Flask
from werkzeug.security import generate_password_hash

from app.config import Config
from app.extensions import csrf, db, login_manager
from app.logging_config import configure_logging
from controllers.auth_controller import auth_bp
from controllers.dashboard_controller import dashboard_bp
from controllers.employee_controller import employee_bp
from controllers.error_controller import error_bp
from controllers.excel_controller import excel_bp
from controllers.recipient_controller import recipient_bp
from models.entities import User
from services.scheduler_service import SchedulerService


def create_app(config_class: type[Config] = Config) -> Flask:
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_object(config_class)

    configure_logging(app)
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        db.create_all()

    register_blueprints(app)
    register_cli(app)

    if (
        not app.config.get("TESTING")
        and app.config.get("SCHEDULER_ENABLED", True)
        and _should_start_scheduler()
    ):
        SchedulerService(app).start()

    return app


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(employee_bp, url_prefix="/employees")
    app.register_blueprint(recipient_bp, url_prefix="/recipients")
    app.register_blueprint(excel_bp, url_prefix="/excel")
    app.register_blueprint(error_bp)


def register_cli(app: Flask) -> None:
    @app.cli.command("init-db")
    def init_db() -> None:
        db.create_all()
        print("Таблицы базы данных созданы или уже существуют.")

    @app.cli.command("create-admin")
    def create_admin() -> None:
        username = app.config["ADMIN_USERNAME"]
        password = app.config["ADMIN_PASSWORD"]
        existing = User.query.filter_by(username=username).first()
        if existing:
            print(f"Администратор '{username}' уже существует.")
            return
        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            is_active=True,
        )
        db.session.add(user)
        db.session.commit()
        print(f"Администратор '{username}' создан.")


def _should_start_scheduler() -> bool:
    maintenance_commands = {
        "init-db",
        "create-admin",
        "db",
        "shell",
        "routes",
    }
    if len(sys.argv) > 1 and any(command in maintenance_commands for command in sys.argv):
        return False
    return True


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))
