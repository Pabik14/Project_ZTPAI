from flask import Blueprint, render_template, redirect, url_for, session,jsonify, request
from app.handler.dbcreate import create_tables,insert_static_data,insert_users
import psycopg2
import os

views_bp = Blueprint("views", __name__)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://anime_user:anime_password@db/anime_db")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

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
    """Renderuje dashboard z danymi o anime"""

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]
    conn = get_db_connection()
    cur = conn.cursor()

    # Pobranie liczby anime według statusu
    cur.execute("""
        SELECT statuses.name, COUNT(*) 
        FROM anime_list
        JOIN statuses ON anime_list.status_id = statuses.id
        WHERE user_id = %s
        GROUP BY statuses.name
    """, (user_id,))
    status_counts = {row[0]: row[1] for row in cur.fetchall()}

    # Pobranie liczby anime według typu
    cur.execute("""
        SELECT types.name, COUNT(*) 
        FROM anime_list
        JOIN types ON anime_list.type_id = types.id
        WHERE user_id = %s
        GROUP BY types.name
    """, (user_id,))
    type_counts = {row[0]: row[1] for row in cur.fetchall()}

    cur.close()
    conn.close()

    return render_template("dashboard.html", username=session["username"], status_counts=status_counts, type_counts=type_counts)


@views_bp.route("/anime-list")
def anime_list():
    """Renderuje listę anime dla zalogowanego użytkownika"""

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]
    conn = get_db_connection()
    cur = conn.cursor()

    # Pobranie listy anime dla użytkownika
    cur.execute("""
        SELECT anime_list.id, anime_list.anime_name, categories.name, types.name, statuses.name, anime_list.episodes 
        FROM anime_list
        JOIN categories ON anime_list.category_id = categories.id
        JOIN types ON anime_list.type_id = types.id
        JOIN statuses ON anime_list.status_id = statuses.id
        WHERE user_id = %s
    """, (user_id,))
    
    anime_list = [
        {"id": row[0], "anime_name": row[1], "category": row[2], "type": row[3], "status": row[4], "episodes_count": row[5]}
        for row in cur.fetchall()
    ]

    cur.close()
    conn.close()

    return render_template("animelist.html", username=session["username"], anime_list=anime_list)

@views_bp.route("/delete_anime/<int:anime_id>", methods=["DELETE"])
def delete_anime(anime_id):
    """Usuwa anime z listy użytkownika"""
    
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session["user_id"]

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("DELETE FROM anime_list WHERE id = %s AND user_id = %s RETURNING id", (anime_id, user_id))
        deleted = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        if deleted:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Anime not found or unauthorized"}), 403

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@views_bp.route("/add-anime", methods=["GET", "POST"])
def add_anime():
    """Obsługa dodawania anime"""

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]

    if request.method == "POST":
        anime_name = request.form.get("anime_name")
        category = request.form.get("category")
        type_ = request.form.get("type")
        status = request.form.get("status")
        episodes_count = request.form.get("episodes_count")

        try:
            conn = get_db_connection()
            cur = conn.cursor()

            # Pobranie ID kategorii, typu i statusu z bazy
            cur.execute("SELECT id FROM categories WHERE name = %s", (category,))
            category_id = cur.fetchone()
            
            cur.execute("SELECT id FROM types WHERE name = %s", (type_,))
            type_id = cur.fetchone()
            
            cur.execute("SELECT id FROM statuses WHERE name = %s", (status,))
            status_id = cur.fetchone()

            if not category_id or not type_id or not status_id:
                return jsonify({"error": "Invalid category, type, or status"}), 400

            cur.execute("""
                INSERT INTO anime_list (user_id, anime_name, category_id, type_id, status_id, episodes)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, anime_name, category_id[0], type_id[0], status_id[0], episodes_count))

            conn.commit()
            cur.close()
            conn.close()

            return jsonify({"success": True})

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    categories = ["Akcja", "Przygodowe", "Horror", "Fantasy", "Sci-Fi", "Komedia", "Dramat", "Romans", "Shounen", "Shoujo", "Mecha", "Slice of Life", "Mystery", "Thriller", "Sportowe"]
    types = ["TV", "Movie", "OVA", "Special"]
    statuses = ["Watching", "Watched", "Planned", "On hold", "Abandoned"]

    return render_template("addAnime.html", categories=categories, types=types, statuses=statuses)
