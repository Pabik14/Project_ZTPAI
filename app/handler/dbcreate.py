import os
import psycopg2
import bcrypt


# Pobieramy dane do połączenia z bazy z zmiennych środowiskowych
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://anime_user:anime_password@db/anime_db")

def create_tables():
    """Tworzy tabele w bazie danych PostgreSQL"""
    commands = [
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS categories (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50) UNIQUE NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS types (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50) UNIQUE NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS statuses (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50) UNIQUE NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS anime_list (
            id SERIAL PRIMARY KEY,
            user_id INT REFERENCES users(id) ON DELETE CASCADE,
            anime_name VARCHAR(255) NOT NULL,
            category_id INT REFERENCES categories(id) ON DELETE SET NULL,
            type_id INT REFERENCES types(id) ON DELETE SET NULL,
            status_id INT REFERENCES statuses(id) ON DELETE SET NULL,
            episodes INT DEFAULT 0
        )
        """
    ]

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        for command in commands:
            cur.execute(command)
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Baza danych i tabele zostały utworzone!")
    except Exception as e:
        print(f"❌ Błąd podczas tworzenia bazy danych: {e}")

def insert_static_data():
    """Dodaje domyślne wartości do tabel categories, types i statuses"""
    commands = [
        """
        INSERT INTO categories (name) VALUES 
        ('Akcja'), ('Przygodowe'), ('Horror'), ('Fantasy'), ('Sci-Fi'), 
        ('Komedia'), ('Dramat'), ('Romans'), ('Shounen'), ('Shoujo'), 
        ('Mecha'), ('Slice of Life'), ('Mystery'), ('Thriller'), ('Sportowe')
        ON CONFLICT DO NOTHING
        """,
        """
        INSERT INTO types (name) VALUES 
        ('TV'), ('Movie'), ('OVA'), ('Special')
        ON CONFLICT DO NOTHING
        """,
        """
        INSERT INTO statuses (name) VALUES 
        ('Watching'), ('Watched'), ('Planned'), ('On hold'), ('Abandoned')
        ON CONFLICT DO NOTHING
        """
    ]

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        for command in commands:
            cur.execute(command)
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Domyślne dane zostały dodane do tabel categories, types, statuses!")
    except Exception as e:
        print(f"❌ Błąd podczas dodawania danych: {e}")
def hash_password(password):
    """Zwraca zahashowane hasło"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def insert_users():
    """Dodaje domyślnych użytkowników do bazy"""
    users = [
        ("admin", "admin@admin.pl", hash_password("123")),
        ("test", "test@test.pl", hash_password("123")),
        ("test2", "test2@test.pl", hash_password("123"))
    ]

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        for name, email, password in users:
            cur.execute(
                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s) ON CONFLICT (email) DO NOTHING",
                (name, email, password)
            )

        conn.commit()
        cur.close()
        conn.close()
        print("✅ Domyślni użytkownicy zostali dodani do bazy!")
    except Exception as e:
        print(f"❌ Błąd podczas dodawania użytkowników: {e}")

if __name__ == "__main__":
    create_tables()
    insert_static_data()
