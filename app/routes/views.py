from flask import Blueprint, render_template, redirect, url_for, session, jsonify, request
from app.handler.dbcreate import db
from app.handler.dbcreate import User, Anime, Category, Type, Status
from flask_jwt_extended import jwt_required, get_jwt_identity

views_bp = Blueprint("views", __name__)

@views_bp.route("/")
def redirect_home():
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
    user_id=session["user_id"] 
    # Pobranie liczby anime według statusu
    status_counts = (
        db.session.query(Status.name, db.func.count(Anime.id))
        .join(Anime, Anime.status_id == Status.id)
        .filter(Anime.user_id == user_id)
        .group_by(Status.name)
        .all()
    )

    # Pobranie liczby anime według typu
    type_counts = (
        db.session.query(Type.name, db.func.count(Anime.id))
        .join(Anime, Anime.type_id == Type.id)
        .filter(Anime.user_id == user_id)
        .group_by(Type.name)
        .all()
    )

    return render_template(
        "dashboard.html",
        username=session["username"],
        status_counts={row[0]: row[1] for row in status_counts},
        type_counts={row[0]: row[1] for row in type_counts},
    )

@views_bp.route("/anime-list")
def anime_list():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    user_id=session["user_id"] 
    anime_list = (
        db.session.query(
            Anime.id,
            Anime.anime_name,
            Category.name,
            Type.name,
            Status.name,
            Anime.episodes,
        )
        .join(Category, Anime.category_id == Category.id)
        .join(Type, Anime.type_id == Type.id)
        .join(Status, Anime.status_id == Status.id)
        .filter(Anime.user_id == user_id)
        .all()
    )

    return render_template(
        "animelist.html",
        username=session["username"],
        anime_list=[
            {
                "id": row[0],
                "anime_name": row[1],
                "category": row[2],
                "type": row[3],
                "status": row[4],
                "episodes_count": row[5],
            }
            for row in anime_list
        ],
    )

@views_bp.route("/delete_anime/<int:anime_id>", methods=["DELETE"])
def delete_anime(anime_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    user_id=session["user_id"] 

    anime = Anime.query.filter_by(id=anime_id, user_id=user_id).first()

    if anime:
        db.session.delete(anime)
        db.session.commit()
        return jsonify({"success": True})
    else:
        return jsonify({"error": "Anime not found or unauthorized"}), 403

@views_bp.route("/add-anime", methods=["GET", "POST"])
def add_anime():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    user_id=session["user_id"] 
    
    if request.method == "POST":
        anime_name = request.form.get("anime_name")
        category_name = request.form.get("category")
        type_name = request.form.get("type")
        status_name = request.form.get("status")
        episodes_count = request.form.get("episodes_count")

        category = Category.query.filter_by(name=category_name).first()
        type_ = Type.query.filter_by(name=type_name).first()
        status = Status.query.filter_by(name=status_name).first()

        if not category or not type_ or not status:
            return jsonify({"error": "Invalid category, type, or status"}), 400

        new_anime = Anime(
            user_id=user_id,
            anime_name=anime_name,
            category_id=category.id,
            type_id=type_.id,
            status_id=status.id,
            episodes=episodes_count,
        )

        db.session.add(new_anime)
        db.session.commit()

        return jsonify({"success": True})

    categories = [cat.name for cat in Category.query.all()]
    types = [t.name for t in Type.query.all()]
    statuses = [s.name for s in Status.query.all()]

    return render_template(
        "addAnime.html",
        categories=categories,
        types=types,
        statuses=statuses,
    )
