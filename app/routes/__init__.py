from flask import Flask
from app.routes.views import views_bp
from app.routes.auth import auth_bp
from app.routes.api import api_bp
from app.routes.admin import admin_bp
from app.handler.dbcreate import *
from flask_jwt_extended import JWTManager
import os

def create_app():
    app = Flask(__name__, template_folder="templates")
    app.secret_key = "supersecretkey"

    # Inicjalizacja bazy danych
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "postgresql://anime_user:anime_password@db/anime_db")
    db.init_app(app)
    with app.app_context():
         db.create_all()
         insert_static_data()
         insert_users()
        # Konfiguracja JWT
    app.config["JWT_SECRET_KEY"] = "supersecretjwtkey"  # Użyj bardziej bezpiecznego klucza!
    jwt = JWTManager(app)  # 🔥 To jest najważniejsze!
    app.register_blueprint(views_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp, url_prefix="/api")  # REST API
    app.register_blueprint(admin_bp)  # ✅ Rejestrujemy admina
    return app
