import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

def send_email(
    from_email: str,
    from_name: str | None,
    to_emails: list[str],
    subject: str,
    body: str,
):
    # Gmail wants the FROM to match the authenticated user for best deliverability
    smtp_user = os.getenv("SMTP_USER")
    if not smtp_user:
        raise RuntimeError("SMTP_USER is not set in .env")

    # Force sender to be the Gmail account (you can still use a friendly name)
    sender_email = smtp_user
    sender = f"{from_name} <{sender_email}>" if from_name else sender_email

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(to_emails)

    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_pass = os.getenv("SMTP_PASSWORD")

    if not smtp_pass:
        raise RuntimeError("SMTP_PASSWORD is not set in .env")

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(sender_email, to_emails, msg.as_string())
