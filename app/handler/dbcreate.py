import os
import bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask

# Inicjalizacja aplikacji Flask
app = Flask(__name__)

# Konfiguracja bazy danych
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "postgresql://anime_user:anime_password@db/anime_db")

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)

class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

class Type(db.Model):
    __tablename__ = "types"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

class Status(db.Model):
    __tablename__ = "statuses"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

class Anime(db.Model):
    __tablename__ = "anime_list"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    anime_name = db.Column(db.String(255), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey("types.id"), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey("statuses.id"), nullable=False)
    episodes = db.Column(db.Integer, default=0)

    user = db.relationship("User", backref="anime_list")
    category = db.relationship("Category", backref="anime_list")
    type = db.relationship("Type", backref="anime_list")
    status = db.relationship("Status", backref="anime_list")

def hash_password(password):
    """Zwraca zahashowane hasło"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def insert_static_data():
    """Dodaje domyślne wartości do tabel categories, types i statuses"""
    categories = ["Akcja", "Przygodowe", "Horror", "Fantasy", "Sci-Fi", 
                  "Komedia", "Dramat", "Romans", "Shounen", "Shoujo", 
                  "Mecha", "Slice of Life", "Mystery", "Thriller", "Sportowe"]
    types = ["TV", "Movie", "OVA", "Special"]
    statuses = ["Watching", "Watched", "Planned", "On Hold", "Abandoned"]

    for name in categories:
        if not Category.query.filter_by(name=name).first():
            db.session.add(Category(name=name))
    
    for name in types:
        if not Type.query.filter_by(name=name).first():
            db.session.add(Type(name=name))
    
    for name in statuses:
        if not Status.query.filter_by(name=name).first():
            db.session.add(Status(name=name))

    db.session.commit()
    print("Domyślne dane dodane!")

def insert_users():
    """Dodaje domyślnych użytkowników do bazy"""
    users = [
        ("admin", "admin@admin.pl", hash_password("123")),
        ("test", "test@test.pl", hash_password("123")),
        ("test2", "test2@test.pl", hash_password("123"))
    ]

    for name, email, password in users:
        if not User.query.filter_by(email=email).first():
            db.session.add(User(name=name, email=email, password=password))
    
    db.session.commit()
    print("Domyślni użytkownicy zostali dodani!")

