import os
import bcrypt
import jwt
import datetime
import pika
import json
from flask import Blueprint, request, render_template, redirect, url_for, session, jsonify
from app.handler.dbcreate import db
from app.handler.dbcreate import User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, set_access_cookies

auth_bp = Blueprint("auth", __name__)

SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")

def hash_password(password):
    """Zwraca zahashowane hasło"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed_password):
    """Sprawdza poprawność hasła"""
    try:
        return bcrypt.checkpw(password.encode(), hashed_password.encode())
    except ValueError:
        print("Błąd: Hasło w bazie nie jest poprawnie zahashowane!")
        return False

def send_to_queue(email, username):
    """Dodaje zadanie wysyłki e-maila do kolejki RabbitMQ"""
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")  # Pobiera host z ENV

    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
        channel = connection.channel()

        # Tworzymy trwałą kolejkę
        channel.queue_declare(queue="email_queue", durable=True)

        # Wysyłamy wiadomość do kolejki w formacie JSON
        message = json.dumps({"email": email, "username": username})
        channel.basic_publish(
            exchange="",
            routing_key="email_queue",
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2  # Zapewnia, że wiadomość przetrwa restart RabbitMQ
            )
        )

        print(f"Zadanie wysyłki e-maila dla {email} wysłane do RabbitMQ")
        connection.close()
    
    except Exception as e:
        print(f"Błąd wysyłania wiadomości do RabbitMQ: {e}")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Obsługuje rejestrację użytkownika"""
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not name or not email or not password or password != confirm_password:
            return render_template("register.html", error="Błąd: Wszystkie pola są wymagane i hasła muszą się zgadzać!")

        if User.query.filter_by(email=email).first():
            return render_template("register.html", error="Użytkownik o tym e-mailu już istnieje!")

        hashed_password = hash_password(password)
        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        print("Rejestracja udana! Przekierowanie na logowanie.")
        return redirect(url_for("auth.login"))

    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Obsługuje logowanie użytkownika"""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            return render_template("login.html", error="Wszystkie pola są wymagane!")

        user = User.query.filter_by(email=email).first()

        if not user or not check_password(password, user.password):
            return render_template("login.html", error="Nieprawidłowy e-mail lub hasło!")

        # Określenie roli użytkownika
        role = "admin" if user.email == "admin@admin.pl" else "user"

        # Tworzymy token JWT
        token = create_access_token(identity={"user_id": user.id, "role": role})

        # Zapisujemy dane użytkownika w sesji
        session["user_id"] = user.id
        session["username"] = user.name
        session["role"] = role
        session["token"] = token
    
        print(f"Logowanie udane! Rola: {role}")
        send_to_queue(user.email, user.name)

        # Przekierowanie do odpowiedniego panelu
        if role == "admin":
            return redirect(url_for("admin.admin_panel"))  
        else:
            return redirect(url_for("views.dashboard"))

    return render_template("login.html")

@auth_bp.route("/logout", methods=["GET", "POST"])
def logout():
    """Wylogowanie użytkownika i przekierowanie na stronę główną"""
    session.clear()
    return redirect(url_for("views.home"))

