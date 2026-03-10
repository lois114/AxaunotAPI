import os
import smtplib
from email.message import EmailMessage
from pathlib import Path


def send_email_with_attachment(file_path: str):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    email_from = os.getenv("EMAIL_FROM")
    email_to = os.getenv("EMAIL_TO")

    if not all([smtp_host, smtp_port, smtp_user, smtp_password, email_from, email_to]):
        raise ValueError("Variables SMTP / email manquantes.")

    file = Path(file_path)
    if not file.exists():
        raise FileNotFoundError(f"Fichier introuvable : {file_path}")

    msg = EmailMessage()
    msg["Subject"] = f"Export Axonaut - {file.stem}"
    msg["From"] = email_from
    msg["To"] = email_to
    msg.set_content("Bonjour,\n\nVoici l'export Axonaut automatique du jour.\n")

    with open(file, "rb") as f:
        file_data = f.read()
        msg.add_attachment(
            file_data,
            maintype="application",
            subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=file.name,
        )

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)

    print(f"Email envoyé à {email_to}")
