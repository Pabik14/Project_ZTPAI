from flask import Flask
from app.routes.views import views_bp

def create_app():
    app = Flask(__name__, template_folder="templates")
    app.register_blueprint(views_bp)
    return app
