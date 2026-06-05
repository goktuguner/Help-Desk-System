"""Email service for sending ticket notifications."""

import os
import smtplib
from email.message import EmailMessage

from app.models import Ticket, User


def send_ticket_created_email(user: User, ticket: Ticket) -> None:
    """Send an email notification when a ticket is created."""

    email_host = os.getenv("EMAIL_HOST")
    email_port = int(os.getenv("EMAIL_PORT", "587"))
    email_user = os.getenv("EMAIL_USER")
    email_password = os.getenv("EMAIL_PASSWORD")

    if not email_host or not user.email:
        print("Email settings are missing or user email is missing. Ticket email was not sent.")
        return

    message = EmailMessage()
    message["From"] = email_user
    message["To"] = user.email
    message["Subject"] = "Ticket Created Successfully"

    message.set_content(f"""
Hello {user.name if hasattr(user, "name") and user.name else ""},

Your support ticket has been created successfully.

Ticket ID: {ticket.id}
Title: {ticket.title}
Priority: {ticket.priority}
Status: {ticket.status}

Our support team will review your request as soon as possible.

Best regards,
Help Desk Team
""")

    with smtplib.SMTP(email_host, email_port) as server:
        if email_user and email_password and email_host != "mailpit":
            server.starttls()
            server.login(email_user, email_password)

        server.send_message(message)
