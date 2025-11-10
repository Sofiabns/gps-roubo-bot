import smtplib
import os
from email.message import EmailMessage
from dotenv import load_dotenv
load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SENDER = os.getenv("EMAIL_SENDER")
PASSWORD = os.getenv("EMAIL_PASSWORD")

def send_alert(receiver: str, subject: str, body: str):
    if not SENDER or not PASSWORD:
        raise RuntimeError("EMAIL_SENDER and EMAIL_PASSWORD must be set in .env")
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SENDER
    msg["To"] = receiver
    msg.set_content(body)
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(SENDER, PASSWORD)
        smtp.send_message(msg)
