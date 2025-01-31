from flask import jsonify, request, session
from flask_restx import Namespace, Resource, fields
from app.handler.dbcreate import db, User, Anime  # Importujemy SQLAlchemy modele
import bcrypt

# Tworzymy przestrzeń nazw (namespace) dla API
api = Namespace("api", description="Operacje API aplikacji Anime Tracker")

# Definicje modeli do Swagger UI
user_model = api.model("User", {
    "name": fields.String(required=True, description="Nazwa użytkownika"),
    "email": fields.String(required=True, description="Adres e-mail"),
    "password": fields.String(required=True, description="Hasło")
})

anime_model = api.model("Anime", {
    "user_id": fields.Integer(required=True, description="ID użytkownika"),
    "anime_name": fields.String(required=True, description="Nazwa anime")
})

# =================== UŻYTKOWNICY =================== #

@api.route("/users")
class UsersResource(Resource):
    """Operacje na użytkownikach"""

    def get(self):
        """Zwraca listę użytkowników"""
        try:
            users = User.query.all()
            return jsonify([{"id": user.id, "name": user.name, "email": user.email} for user in users])
        except Exception as e:
            return {"error": f"Błąd pobierania użytkowników: {e}"}, 500

    @api.expect(user_model)
    def post(self):
        """Dodaje nowego użytkownika"""
        data = request.json
        if not data.get("name") or not data.get("email") or not data.get("password"):
            return {"error": "Wszystkie pola są wymagane"}, 400
        
        if User.query.filter_by(email=data["email"]).first():
            return {"error": "Użytkownik o podanym e-mailu już istnieje"}, 400
        
        new_user = User(name=data["name"], email=data["email"], password=data["password"])
        db.session.add(new_user)
        db.session.commit()
        return {"message": "Użytkownik dodany", "id": new_user.id}, 201

@api.route("/users/<int:id>")
class UserResource(Resource):
    """Operacje na konkretnym użytkowniku"""

    def delete(self, id):
        """Usuwa użytkownika"""
        user = User.query.get(id)
        if not user:
            return {"error": "Użytkownik nie istnieje"}, 404
        
        db.session.delete(user)
        db.session.commit()
        return {"message": "Użytkownik usunięty"}, 200

# =================== ANIME =================== #

@api.route("/anime")
class AnimeResource(Resource):
    """Operacje na anime"""

    def get(self):
        """Zwraca listę anime"""
        try:
            anime_list = Anime.query.all()
            return jsonify([{"id": anime.id, "name": anime.anime_name, "user_id": anime.user_id} for anime in anime_list])
        except Exception as e:
            return {"error": f"Błąd pobierania anime: {e}"}, 500

    @api.expect(anime_model)
    def post(self):
        """Dodaje nowe anime"""
        data = request.json
        if not data.get("user_id") or not data.get("anime_name"):
            return {"error": "Wszystkie pola są wymagane"}, 400

        new_anime = Anime(user_id=data["user_id"], anime_name=data["anime_name"])
        db.session.add(new_anime)
        db.session.commit()
        return {"message": "Anime dodane", "id": new_anime.id}, 201

@api.route("/anime/<int:id>")
class AnimeItemResource(Resource):
    """Operacje na konkretnym anime"""

    def delete(self, id):
        """Usuwa anime"""
        anime = Anime.query.get(id)
        if not anime:
            return {"error": "Anime nie istnieje"}, 404
        
        db.session.delete(anime)
        db.session.commit()
        return {"message": "Anime usunięte"}, 200


# Definicje modeli do Swagger UI
login_model = api.model("Login", {
    "email": fields.String(required=True, description="Adres e-mail"),
    "password": fields.String(required=True, description="Hasło")
})

# =================== LOGOWANIE =================== #

@api.route("/auth/login")
class AuthLoginResource(Resource):
    """Logowanie użytkownika"""

    @api.expect(login_model)
    def post(self):
        """Logowanie użytkownika"""
        data = request.json
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return {"error": "Wszystkie pola są wymagane!"}, 400

        user = User.query.filter_by(email=email).first()
        if not user or not bcrypt.checkpw(password.encode(), user.password.encode()):
            return {"error": "Nieprawidłowe dane logowania!"}, 401

        # Zapisanie użytkownika w sesji
        session["user_id"] = user.id
        session["username"] = user.name
        session["email"] = user.email

        return {"message": "Zalogowano pomyślnie!", "user": {"id": user.id, "name": user.name, "email": user.email}}, 200

@api.route("/auth/session")
class AuthSessionResource(Resource):
    """Sprawdza, czy użytkownik jest zalogowany"""

    def get(self):
        """Zwraca dane zalogowanego użytkownika"""
        if "user_id" not in session:
            return {"error": "Brak aktywnej sesji!"}, 401

        return {
            "message": "Użytkownik zalogowany",
            "user": {
                "id": session["user_id"],
                "name": session["username"],
                "email": session["email"]
            }
        }, 200

@api.route("/auth/logout")
class AuthLogoutResource(Resource):
    """Wylogowanie użytkownika"""

    def post(self):
        """Czyści sesję użytkownika"""
        session.clear()
        return {"message": "Wylogowano pomyślnie!"}, 200