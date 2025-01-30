from flask import Blueprint, jsonify, request
import psycopg2
import os

api_bp = Blueprint("api", __name__)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://anime_user:anime_password@db/anime_db")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

@api_bp.route("/users", methods=["GET"])
def get_users():
    """Zwraca listę użytkowników"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email FROM users")
    users = [{"id": row[0], "name": row[1], "email": row[2]} for row in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(users)

@api_bp.route("/anime", methods=["GET"])
def get_anime():
    """Zwraca listę anime"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, anime_name FROM anime_list")
    anime = [{"id": row[0], "name": row[1]} for row in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(anime)
