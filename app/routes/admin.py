from flask import Blueprint, render_template, redirect, url_for, session, jsonify, request,send_file
import psycopg2
import os
import shutil


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://anime_user:anime_password@db/anime_db")
DB_BACKUP_PATH = "/tmp/anime_db_backup.sql"

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

@admin_bp.route("/")
def admin_panel():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email FROM users")
    users = [{"id": row[0], "name": row[1], "email": row[2]} for row in cur.fetchall()]
    cur.close()
    conn.close()

    return render_template("adminPanel.html", users=users)

@admin_bp.route("/delete_user/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    if "user_id" not in session or session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    
    
@admin_bp.route("/download_database", methods=["POST"])
def download_database():
    """Admin może pobrać kopię zapasową bazy PostgreSQL"""
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("auth.login"))

    try:
        dump_command = f"pg_dump {DATABASE_URL} -F c -f {DB_BACKUP_PATH}"
        result = os.system(dump_command)

        if result != 0 or not os.path.exists(DB_BACKUP_PATH):
            return "Błąd tworzenia kopii bazy danych", 500

        return send_file(DB_BACKUP_PATH, as_attachment=True, download_name="anime_db_backup.sql")
    
    except Exception as e:
        return f"Błąd: {str(e)}", 500