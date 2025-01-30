import os
import psycopg2
import bcrypt
import jwt
import datetime
from flask import Blueprint, request, render_template, redirect, url_for, session, jsonify

auth_bp = Blueprint("auth", __name__)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://anime_user:anime_password@db/anime_db")
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed_password):
    """Sprawdza poprawność hasła"""
    try:
        return bcrypt.checkpw(password.encode(), hashed_password.encode())
    except ValueError:
        print("❌ Błąd: Hasło w bazie nie jest poprawnie zahashowane!")
        return False


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Obsługuje rejestrację użytkownika"""
    if request.method == "POST":
        try:
            name = request.form.get("name")
            email = request.form.get("email")
            password = request.form.get("password")
            confirm_password = request.form.get("confirm_password")

            if not name or not email or not password or password != confirm_password:
                return render_template("register.html", error="Błąd: Wszystkie pola są wymagane i hasła muszą się zgadzać!")

            hashed_password = hash_password(password)

            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute(
                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s) ON CONFLICT (email) DO NOTHING RETURNING id",
                (name, email, hashed_password),
            )
            user_id = cur.fetchone()
            conn.commit()
            cur.close()
            conn.close()

            if not user_id:
                return render_template("register.html", error="Użytkownik o tym e-mailu już istnieje!")

            print("✅ Rejestracja udana! Przekierowanie na logowanie.")
            return redirect(url_for("auth.login"))

        except Exception as e:
            print(f"❌ Błąd rejestracji: {str(e)}")
            return render_template("register.html", error=f"Błąd: {str(e)}")

    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Obsługuje logowanie użytkownika"""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            return render_template("login.html", error="Wszystkie pola są wymagane!")

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, name, email, password FROM users WHERE email = %s", (email,))
            user = cur.fetchone()
            cur.close()
            conn.close()

            if not user or not check_password(password, user[3]):
                return render_template("login.html", error="Nieprawidłowy e-mail lub hasło!")

            # Określenie roli użytkownika
            role = "admin" if user[2] == "admin@admin.pl" else "user"

            # Tworzymy token JWT
            token = jwt.encode(
                {"user_id": user[0], "role": role, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)},
                SECRET_KEY,
                algorithm="HS256"
            )

            # Zapisujemy dane użytkownika w sesji
            session["user_id"] = user[0]
            session["username"] = user[1]
            session["role"] = role
            session["token"] = token

            print(f"✅ Logowanie udane! Rola: {role}")

            # Przekierowanie do odpowiedniego panelu
            if role == "admin":
                return redirect(url_for("admin.admin_panel"))  # ✅ Poprawiona nazwa blueprinta!
            else:
                return redirect(url_for("views.dashboard"))


        except Exception as e:
            return render_template("login.html", error=f"Błąd logowania: {str(e)}")

    return render_template("login.html")

@auth_bp.route("/logout", methods=["POST"])
def logout():
    """Wylogowanie użytkownika i przekierowanie na stronę główną"""
    session.clear()
    return redirect(url_for("views.home"))

