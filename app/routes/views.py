from flask import Blueprint, render_template, redirect, url_for

views_bp = Blueprint("views", __name__)

@views_bp.route("/")
def redirect_home():
    return redirect(url_for("/home"))

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
    return render_template("dashboard.html")

@views_bp.route("/anime-list")
def anime_list():
    return render_template("animelist.html")

@views_bp.route("/admin-panel")
def admin_panel():
    return render_template("adminPanel.html")

@views_bp.route("/add-anime")
def add_anime():
    return render_template("addAnime.html")
