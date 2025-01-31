from flask import Flask
from app.routes.views import views_bp
from app.routes.auth import auth_bp
from app.routes.api import api as api_ns
from app.routes.admin import admin_bp
from app.handler.dbcreate import *
from flask_jwt_extended import JWTManager
import os
from flask_restx import Api


def create_app():
    app = Flask(__name__, template_folder="templates")
    app.secret_key = "supersecretkey"
    app.config["RESTX_MASK_SWAGGER"] = False  

    api = Api(app, version="1.0", title="Anime Tracker API", description="API do zarządzania anime", doc="/swagger")
    # Inicjalizacja bazy danych
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "postgresql://anime_user:anime_password@db/anime_db")
    db.init_app(app)
    with app.app_context():
         db.create_all()
         insert_static_data()
         insert_users()
        # Konfiguracja JWT
    app.config["JWT_SECRET_KEY"] = "supersecretjwtkey" 
    jwt = JWTManager(app) 
    app.register_blueprint(views_bp)
    app.register_blueprint(auth_bp)
    api.add_namespace(api_ns, path="/api")  # api
    app.register_blueprint(admin_bp)  #rejestrujemy admina
    return app
