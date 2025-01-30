from flask import Flask
from app.routes.views import views_bp
from app.routes.auth import auth_bp
from app.routes.api import api_bp
from app.routes.admin import admin_bp
def create_app():
    app = Flask(__name__, template_folder="templates")
    app.secret_key = "supersecretkey"

    app.register_blueprint(views_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp, url_prefix="/api")  # REST API
    app.register_blueprint(admin_bp)  # ✅ Rejestrujemy admina
    return app
