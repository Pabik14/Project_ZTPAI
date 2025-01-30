from flask import Blueprint, render_template, redirect, url_for, session
from app.handler.dbcreate import create_tables,insert_static_data,insert_users

views_bp = Blueprint("views", __name__)

@views_bp.route("/")
def redirect_home():
    return redirect(url_for("views.home")) 


@views_bp.route("/loadDB")
def db_crate():
    create_tables()
    insert_static_data()
    insert_users()
    return redirect(url_for("views.home"))

@views_bp.route("/home")
def home():
    return render_template("home.html")

@views_bp.route("/login")
def login():
    return render_template("login.html")

@views_bp.route("/register")
def register():
    return render_template("register.html")

@views_bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return render_template("dashboard.html", username=session["username"])


@views_bp.route("/anime-list")
def anime_list():
    return render_template("animelist.html")

@views_bp.route("/admin")
def admin_panel():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("auth.login"))
    return render_template("adminPanel.html", username=session["username"])

@views_bp.route("/add-anime")
def add_anime():
    return render_template("addAnime.html")
