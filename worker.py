import pika
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")


SMTP_SERVER = "smtp.gmail.com"  
SMTP_PORT = 587
SMTP_EMAIL = "test@gmail.com"  
SMTP_PASSWORD = "testowehaslo"  
def send_email(email, username):
    """Wysyła e-mail powitalny do użytkownika"""
    subject = "Witaj w Anime Tracker!"
    body = f"Cześć {username},\n\nDziękujemy za zalogowanie się do Anime Tracker! Miłego korzystania. 🎉\n\nPozdrawiamy,\nZespół Anime Tracker"

    msg = MIMEMultipart()
    msg["From"] = SMTP_EMAIL
    msg["To"] = email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_EMAIL, email, msg.as_string())
        server.quit()
        print(f"📩 E-mail wysłany do {email}")
    except Exception as e:
        print(f"❌ Błąd wysyłania e-maila: {e}")

def callback(ch, method, properties, body):
    """Obsługuje wiadomości z kolejki RabbitMQ"""
    data = json.loads(body)
    email = data["email"]
    username = data["username"]
    print(f"📥 Odebrano wiadomość dla: {email}")

    send_email(email, username)

    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_worker():
    """Uruchamia worker do obsługi RabbitMQ"""
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()

    channel.queue_declare(queue="email_queue")
    channel.basic_consume(queue="email_queue", on_message_callback=callback)

    print("🔄 Worker nasłuchuje kolejki `email_queue`...")
    channel.start_consuming()

if __name__ == "__main__":
    start_worker()
