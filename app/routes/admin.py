from flask import Blueprint, render_template, redirect, url_for, session, jsonify, request, send_file
from app.handler.dbcreate import db
from app.handler.dbcreate import User
import os


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")
DB_BACKUP_PATH = "/tmp/anime_db_backup.sql"

@admin_bp.route("/")
def admin_panel():
    """Panel admina – wyświetla listę użytkowników"""
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("auth.login"))

    users = User.query.with_entities(User.id, User.name, User.email).all()
    users_list = [{"id": user.id, "name": user.name, "email": user.email} for user in users]

    return render_template("adminPanel.html", users=users_list)

@admin_bp.route("/delete_user/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    """Usuwa użytkownika (tylko dla admina)"""
    if "user_id" not in session or session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    try:
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return jsonify({"success": True})
        else:
            return jsonify({"error": "User not found"}), 404

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)})

@admin_bp.route("/download_database", methods=["POST"])
def download_database():
    """Admin może pobrać kopię zapasową bazy PostgreSQL"""
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("auth.login"))

    try:
        dump_command = f"pg_dump {os.getenv('DATABASE_URL')} -F c -f {DB_BACKUP_PATH}"
        result = os.system(dump_command)

        if result != 0 or not os.path.exists(DB_BACKUP_PATH):
            return "Błąd tworzenia kopii bazy danych", 500

        return send_file(DB_BACKUP_PATH, as_attachment=True, download_name="anime_db_backup.sql")
    
    except Exception as e:
        return f"Błąd: {str(e)}", 500
