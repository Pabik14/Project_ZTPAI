# Używamy lekkiego obrazu Pythona
FROM python:3.11

# Ustawiamy katalog roboczy w kontenerze
WORKDIR /app

# Kopiujemy pliki aplikacji do kontenera
COPY requirements.txt .

# Instalujemy zależności
RUN pip install --no-cache-dir -r requirements.txt

# Kopiujemy resztę aplikacji
COPY . .

# Ustawiamy zmienną środowiskową, aby Flask działał w trybie produkcyjnym
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production
ENV PYTHONPATH=/app


# Otwieramy port 5000
EXPOSE 5000

# Komenda uruchamiająca aplikację
CMD ["flask", "run"]
