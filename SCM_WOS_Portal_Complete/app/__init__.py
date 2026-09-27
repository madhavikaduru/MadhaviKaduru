import os
from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    # Application Configurations
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:Av@1234@localhost:5432/scm_wos",
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Bind extensions to app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # User loader callback for Flask-Login
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Import and register blueprints inside factory to prevent circular imports
    from .api import api_bp
    from .auth import auth_bp
    from .routes import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(api_bp, url_prefix="/api")

    # Jinja globals
    app.jinja_env.globals["getattr"] = getattr

    return app